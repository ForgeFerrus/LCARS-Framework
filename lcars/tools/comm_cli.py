"""
LCARS Communication CLI Tool
Provides command-line access to contacts, messages, and calls.
"""
import argparse
from lcars.modules.comm import comm_system, Contact, Message, Call


def main():
    parser = argparse.ArgumentParser(description="LCARS Communication CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Contacts
    contact_parser = subparsers.add_parser("add-contact", help="Add a new contact")
    contact_parser.add_argument("--name", required=True)
    contact_parser.add_argument("--faction")
    contact_parser.add_argument("--email")
    contact_parser.add_argument("--phone")
    contact_parser.add_argument("--address")
    contact_parser.add_argument("--notes")

    search_parser = subparsers.add_parser("search-contacts", help="Search contacts")
    search_parser.add_argument("term", required=True)

    # Messages
    msg_send = subparsers.add_parser("send-message", help="Send a message")
    msg_send.add_argument("--sender", required=True)
    msg_send.add_argument("--recipient", required=True)
    msg_send.add_argument("--content", required=True)

    msg_get = subparsers.add_parser("get-messages", help="Get messages for participant")
    msg_get.add_argument("participant", required=True)

    # Calls
    call_start = subparsers.add_parser("start-call", help="Start a call")
    call_start.add_argument("--caller", required=True)
    call_start.add_argument("--callee", required=True)

    call_end = subparsers.add_parser("end-call", help="End a call")
    call_end.add_argument("--call-id", type=int, required=True)
    call_end.add_argument("--duration", type=float, required=True)

    call_get = subparsers.add_parser("get-calls", help="Get calls for participant")
    call_get.add_argument("participant", required=True)

    args = parser.parse_args()

    if args.command == "add-contact":
        contact = Contact(
            name=args.name,
            faction=args.faction,
            email=args.email,
            phone=args.phone,
            address=args.address,
            notes=args.notes
        )
        cid = comm_system.add_contact(contact)
        print(f"Contact added with ID: {cid}")
    elif args.command == "search-contacts":
        results = comm_system.search_contacts(args.term)
        for c in results:
            print(f"[{c.id}] {c.name} | {c.faction} | {c.email} | {c.phone}")
    elif args.command == "send-message":
        mid = comm_system.send_message(args.sender, args.recipient, args.content)
        print(f"Message sent with ID: {mid}")
    elif args.command == "get-messages":
        msgs = comm_system.get_messages(args.participant)
        for m in msgs:
            print(f"[{m.id}] {m.timestamp:.0f} {m.sender} -> {m.recipient}: {m.content} [{m.status}]")
    elif args.command == "start-call":
        call_id = comm_system.start_call(args.caller, args.callee)
        print(f"Call started with ID: {call_id}")
    elif args.command == "end-call":
        comm_system.end_call(args.call_id, args.duration)
        print(f"Call {args.call_id} ended, duration {args.duration}s")
    elif args.command == "get-calls":
        calls = comm_system.get_calls(args.participant)
        for c in calls:
            print(f"[{c.id}] {c.timestamp:.0f} {c.caller} -> {c.callee} duration={c.duration} status={c.status}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
