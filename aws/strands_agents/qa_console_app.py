import os
import sys
from strands import tool
from strands_harness import create_harness

# --- QA Automation Tools ---

@tool
def run_test_suite(test_target: str = "smoke") -> str:
    """Run automated test suites (e.g., unit, integration, smoke, regression, e2e).

    Args:
        test_target: Module name, test suite, or tag ('smoke', 'regression', 'all').
    """
    return (
        f"[TestRunner] Executed test suite for: '{test_target}'.\n"
        f"Passed: 28, Failed: 0, Skipped: 1. Coverage: 92.5%.\n"
        f"Duration: 4.12s. All assertions passed."
    )

@tool
def check_service_health(service_url: str = "https://api.internal/health") -> str:
    """Inspect and verify service endpoint health, dependencies, and response latency.

    Args:
        service_url: URL or endpoint of the service to probe.
    """
    return (
        f"[HealthCheck] Endpoint '{service_url}' returned HTTP 200 OK.\n"
        f"Latency: 35ms. Database: Healthy. Redis Cache: Healthy. Message Queue: Ready."
    )

@tool
def deploy_release_build(environment: str, version_tag: str) -> str:
    """Deploy a verified release build to a target staging or production environment.

    Args:
        environment: Target environment ('staging', 'qa-sandbox', 'production').
        version_tag: Release semver or build tag (e.g., 'v1.4.0').
    """
    return (
        f"[Deployment Pipeline] Successfully triggered deployment of {version_tag} "
        f"to target environment '{environment}'. Build verification tests initiated."
    )

@tool
def query_defect_tracker(component: str) -> str:
    """Query defect tracker for open bug tickets and blockers on a given component.

    Args:
        component: Target module or feature name (e.g. 'auth', 'billing', 'cart').
    """
    return (
        f"[DefectTracker] 0 blocker bugs, 1 minor open bug found for '{component}'.\n"
        f"- BUG-108: Cosmetic alignment on mobile viewport (Severity: Low, Status: In Review)."
    )

def build_qa_harness_agent():
    """Builds and returns a Strands agent using create_harness with QA tools and safety interventions."""
    instructions = (
        "You are an expert QA and Release Engineer assistant. "
        "You evaluate test outcomes, perform health checks, analyze defect trends, "
        "and coordinate test deployments. "
        "Always follow QA gating standards and ask for explicit human confirmation before executing any deployment."
    )

    # Configure any available LLM provider or fallback
    model = None
    if os.getenv("OPENAI_API_KEY"):
        try:
            from strands.models.openai import OpenAIModel
            model = OpenAIModel(
                client_args={"api_key": os.getenv("OPENAI_API_KEY")},
                model_id=os.getenv("OPENAI_MODEL_ID", "gpt-4o"),
            )
        except ImportError:
            pass
    elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        try:
            from strands.models.gemini import GeminiModel
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            model = GeminiModel(
                client_args={"api_key": api_key},
                model_id=os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash"),
            )
        except ImportError:
            pass

    harness_kwargs = {
        "instructions": instructions,
        "tools": [
            run_test_suite,
            check_service_health,
            query_defect_tracker,
            deploy_release_build,
        ],
        # Interventions: require explicit confirmation before sensitive actions (like deployments)
        "interventions": "Ask for approval before triggering any deployment to staging or production.",
    }

    if model:
        harness_kwargs["model"] = model

    return create_harness(**harness_kwargs)

def print_banner():
    print("=" * 72)
    print("   QA & Release Engineering Assistant (Strands Harness Console)   ")
    print("=" * 72)
    print("Commands:")
    print("  - Type any QA request (e.g., test runs, health probes, bug reports).")
    print("  - Type 'help' to view sample prompts.")
    print("  - Type 'exit' or 'quit' to terminate.")
    print("-" * 72)

def print_help():
    print("\nSample QA Prompts:")
    print("  1. 'Run the regression test suite for checkout.'")
    print("  2. 'Check service health for our auth gateway at https://auth.api/health.'")
    print("  3. 'Are there any open defects in the billing component?'")
    print("  4. 'Deploy v2.1.0 to staging and run smoke tests.' (Triggers intervention flow)\n")

def main():
    print_banner()

    agent = None
    try:
        agent = build_qa_harness_agent()
    except Exception as e:
        print(f"\n[Notice] Harness agent using default provider fallback: {e}")
        print("Set OPENAI_API_KEY or AWS credentials for full multi-turn LLM reasoning.\n")

    while True:
        try:
            user_input = input("\n[QA-Console] > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "q"):
                print("\nExiting QA Console. Have a great day!")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            if agent:
                print("\n[Harness Agent Thinking & Executing...]")
                response = agent(user_input)
                print("\n[QA Agent Response]:")
                print(response)
            else:
                # Standalone simulation fallback for quick offline evaluation
                print(f"\n[Simulated Console Response for: '{user_input}']")
                lowered = user_input.lower()
                if "deploy" in lowered:
                    print("[Intervention]: Deployment requires confirmation. Confirmation granted.")
                    print(deploy_release_build("staging", "v1.0.0-rc1"))
                elif "test" in lowered:
                    print(run_test_suite("smoke"))
                elif "health" in lowered or "check" in lowered:
                    print(check_service_health())
                elif "defect" in lowered or "bug" in lowered:
                    print(query_defect_tracker("auth"))
                else:
                    print("Query analyzed. Configure API credentials to enable dynamic LLM tool orchestration.")

        except (KeyboardInterrupt, EOFError):
            print("\n\nSession terminated by user. Exiting.")
            break
        except Exception as err:
            print(f"\n[Error executing query]: {err}")

if __name__ == "__main__":
    main()
