import os
import sys

def print_banner():
    banner = """
========================================================================
       CrewAI Email Classifier & Action Assistant (Console App)       
========================================================================
Commands:
  - Enter or paste an email snippet to classify and draft actions.
  - Type 'samples' or 'help' to view pre-loaded email test cases.
  - Type 'exit' or 'quit' to terminate.
------------------------------------------------------------------------
"""
    print(banner.strip())


SAMPLE_EMAILS = [
    {
        "id": "1",
        "title": "Production Server Outage (Urgent / Bug)",
        "content": (
            "From: ops-alert@acme.com\n"
            "Subject: CRITICAL: Production DB connection pool exhausted on payment-gateway\n\n"
            "Hi Support Team, our payment service is returning 500 errors across all checkout "
            "flows. Transactions are failing and customers cannot complete orders. Please investigate immediately."
        ),
    },
    {
        "id": "2",
        "title": "Enterprise Sales Lead (Sales Inquiry)",
        "content": (
            "From: j.smith@enterprise-corp.com\n"
            "Subject: Enterprise Tier Pricing & 500-Seat License Quote\n\n"
            "Hello, our organization is looking to roll out your platform to 500 engineers next quarter. "
            "Could we schedule a call with your sales team this Thursday to review enterprise security, SSO, and volume pricing?"
        ),
    },
    {
        "id": "3",
        "title": "Subscription Billing Question (Customer Support)",
        "content": (
            "From: alice.jones@gmail.com\n"
            "Subject: Double charge on invoice #INV-49201\n\n"
            "Hi, I noticed two charges of $49 on my credit card statement for last month. "
            "Could you check my account and refund the extra charge? My account email is alice.jones@gmail.com."
        ),
    },
    {
        "id": "4",
        "title": "Cold Marketing Spam (Spam / Low Priority)",
        "content": (
            "From: growth-hack@leadgenerator-fast.biz\n"
            "Subject: Boost your B2B leads 10x with our automated scraping bot!\n\n"
            "Dear Founder, buy our list of 5 million verified decision makers today for only $99! Click here to claim your discount."
        ),
    },
]


def print_help():
    print("\n--- Available Sample Emails ---")
    for sample in SAMPLE_EMAILS:
        print(f"[{sample['id']}] {sample['title']}")
    print("\nTip: You can type 'sample 1', 'sample 2', etc., or enter any custom email text.\n")


def build_crew(email_text: str):
    """Initializes CrewAI agents and tasks for email classification and action drafting."""
    try:
        from crewai import Agent, Crew, Process, Task
    except ImportError:
        return None

    # Agent 1: Categorization & Sentiment Specialist
    classifier = Agent(
        role="Email Classifier & Triage Specialist",
        goal="Accurately analyze incoming emails to determine intent, priority, sentiment, and category.",
        backstory=(
            "You are a seasoned triage coordinator with years of experience filtering high-volume "
            "inboxes for tech companies. You spot critical bugs, high-value enterprise leads, "
            "billing inquiries, and unsolicited marketing/spam with pinpoint accuracy."
        ),
        verbose=False,
    )

    # Agent 2: Response Strategy & Action Planner
    action_planner = Agent(
        role="Customer Success & Incident Response Strategist",
        goal="Formulate the next best action, routing department, and a tailored response draft.",
        backstory=(
            "You are an expert customer relations and incident resolution manager. "
            "You know exactly which team should handle each issue (e.g., SRE on-call, Sales AE, Billing), "
            "and you write concise, empathetic, and professional email responses."
        ),
        verbose=False,
    )

    # Task 1: Classification Task
    classification_task = Task(
        description=(
            f"Analyze the following incoming email:\n\n"
            f"\"\"\"\n{email_text}\n\"\"\"\n\n"
            "Provide:\n"
            "1. Primary Category (e.g., Bug/Urgent Incident, Sales Inquiry, Billing & Support, General Feedback, Spam)\n"
            "2. Urgency Level (Critical, High, Medium, Low)\n"
            "3. Sentiment (Frustrated, Inquiring, Neutral, Positive, Negative)\n"
            "4. Executive Key Points (1-2 sentences summarizing the core request/issue)"
        ),
        expected_output="A structured breakdown with Category, Urgency Level, Sentiment, and Key Points.",
        agent=classifier,
    )

    # Task 2: Action & Draft Task
    response_task = Task(
        description=(
            "Based on the classification analysis, produce:\n"
            "1. Recommended Action & Target Team (e.g., Page SRE on-call, Assign to Sales AE, Route to Billing, Auto-archive)\n"
            "2. Recommended SLA / Response Deadline\n"
            "3. Ready-to-send Professional Draft Reply addressing the sender appropriately."
        ),
        expected_output="Target team routing, recommended SLA, and a complete professional draft email.",
        agent=action_planner,
    )

    crew = Crew(
        agents=[classifier, action_planner],
        tasks=[classification_task, response_task],
        process=Process.sequential,
        verbose=False,
    )
    return crew


def simulate_crew_classification(email_text: str):
    """Rule-based simulation fallback when crewai or LLM API keys are not configured."""
    lowered = email_text.lower()

    # Distinct checks for incident / outage vs sales vs billing
    incident_keywords = ["outage", "500 error", "connection pool", "critical", "crash", "incident", "down", "failing"]
    sales_keywords = ["pricing", "license", "enterprise", "sales", "demo", "seat", "quote"]
    billing_keywords = ["charge", "refund", "invoice", "billing", "credit card"]
    spam_keywords = ["discount", "scraping bot", "b2b leads", "claim your discount", "buy our list"]

    if any(k in lowered for k in incident_keywords):
        category = "Critical Incident / Bug Report"
        urgency = "CRITICAL (Immediate Attention)"
        sentiment = "High Anxiety / Urgent"
        team = "SRE & Engineering On-Call Team"
        sla = "< 15 minutes"
        draft = (
            "Subject: Re: Critical Incident Acknowledged [Ticket #INC-0921]\n\n"
            "Hello,\n\n"
            "Thank you for reporting this issue. Our site reliability engineering team has been "
            "paged and is actively investigating the error. We will keep you updated via status alerts "
            "and follow up directly once service is restored.\n\n"
            "Best regards,\nIncident Response Operations"
        )
    elif any(k in lowered for k in sales_keywords):
        category = "Sales Inquiry / Enterprise Lead"
        urgency = "High (Business Priority)"
        sentiment = "Inquiring / High Intent"
        team = "Enterprise Account Executives"
        sla = "< 2 hours"
        draft = (
            "Subject: Re: Enterprise Tier Pricing & Platform Consultation\n\n"
            "Hello,\n\n"
            "Thank you for your interest! We would be delighted to set up a consultation with you "
            "to review enterprise licensing, security compliance, and volume pricing.\n"
            "Please select a convenient time slot via our team calendar link: [Schedule Link].\n\n"
            "Looking forward to speaking with you!\nEnterprise Sales Team"
        )
    elif any(k in lowered for k in billing_keywords):
        category = "Billing & Financial Support"
        urgency = "Medium"
        sentiment = "Concerned / Inquiring"
        team = "Billing & Customer Care"
        sla = "< 4 hours"
        draft = (
            "Subject: Re: Inquiry regarding your billing statement\n\n"
            "Hello,\n\n"
            "Thank you for reaching out. We have opened a review for your account regarding "
            "the reported duplicate charge. Our billing team is verifying the transaction history "
            "and will initiate any applicable refund within 1-2 business days.\n\n"
            "Sincerely,\nBilling Support Team"
        )
    elif any(k in lowered for k in spam_keywords):
        category = "Unsolicited Cold Pitch / Spam"
        urgency = "Low"
        sentiment = "Promotional"
        team = "Spam Filter / Auto-Archive"
        sla = "N/A (No action needed)"
        draft = "[Action: Filter to Spam folder and add sender domain to blocklist. No response required.]"
    else:
        category = "General Inquiry"
        urgency = "Medium"
        sentiment = "Neutral"
        team = "General Support Desk"
        sla = "< 24 hours"
        draft = (
            "Subject: Re: Your Inquiry\n\n"
            "Hello,\n\n"
            "Thank you for contacting us. We have received your message and routed it to our support team. "
            "A specialist will follow up with detailed information shortly.\n\n"
            "Warm regards,\nCustomer Support Team"
        )

    return f"""
==================== [CLASSIFICATION REPORT] ====================
• Primary Category : {category}
• Urgency Level    : {urgency}
• Sentiment        : {sentiment}
• Target Team      : {team}
• Recommended SLA  : {sla}

===================== [RECOMMENDED ACTION] =====================
• Route To: {team}
• Action  : Log ticket, apply tags, and notify dispatch.

====================== [DRAFT RESPONSE] =======================
{draft}
================================================================
"""


def process_email(email_text: str):
    print("\n[Agents At Work] Analyzing email intent, priority, and draft action...")

    has_crewai = False
    try:
        import crewai
        has_crewai = True
    except ImportError:
        pass

    has_api_key = bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))

    if has_crewai and has_api_key:
        try:
            crew = build_crew(email_text)
            result = crew.kickoff()
            print("\n[CrewAI Multi-Agent Output]:\n")
            print(result)
            return
        except Exception as e:
            print(f"\n[Notice] CrewAI runtime execution encountered: {e}")
            print("Falling back to built-in rule analyzer...\n")

    if not has_crewai:
        print("[Notice] 'crewai' package is not installed in the virtual environment.")
        print("         To enable LLM agent orchestration, run: pip install crewai")
        print("         Displaying deterministic intelligent triage simulation:\n")
    elif not has_api_key:
        print("[Notice] No LLM API key found (OPENAI_API_KEY / ANTHROPIC_API_KEY not set).")
        print("         Displaying deterministic intelligent triage simulation:\n")

    output = simulate_crew_classification(email_text)
    print(output)


def main():
    print_banner()

    while True:
        try:
            user_input = input("\n[Email-Classifier] > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "q"):
                print("\nExiting Email Classifier. Have a great day!")
                break

            if user_input.lower() in ("help", "samples", "sample"):
                print_help()
                continue

            if user_input.lower().startswith("sample "):
                sample_num = user_input.split()[-1]
                found = next((s for s in SAMPLE_EMAILS if s["id"] == sample_num), None)
                if found:
                    print(f"\n--- Loading Sample {found['id']}: {found['title']} ---")
                    print(f"Content:\n{found['content']}\n")
                    process_email(found["content"])
                else:
                    print(f"Sample '{sample_num}' not found. Enter 1, 2, 3, or 4.")
                continue

            # Process custom email content
            process_email(user_input)

        except (KeyboardInterrupt, EOFError):
            print("\n\nSession terminated by user. Exiting.")
            break
        except Exception as err:
            print(f"\n[Error]: {err}")


if __name__ == "__main__":
    main()
