# RupZha Ticket System Design

## Goal
Replace the current three-button ticket panel with a clean two-level support flow that covers community support, complaints/reports, business/client issues, and feedback, while keeping ticket rooms private and scalable.

## User Flow

Public ticket panel -> choose a category -> choose a ticket type -> create one private ticket room.

Categories:
- Support
- Complaints & Reports
- Business / Client
- Feedback

Ticket types:
- Support: General Support, Question / Help, Other / Contact Staff, Account / Role Problem, Ticket Problem, Message / Channel Issue, Bot Problem, Bug Report
- Complaints & Reports: Complaint, Report a Member, Security / Privacy Issue, Moderation Appeal, Punishment Appeal, Negative Feedback / Complaint
- Business / Client: Service Inquiry, Partnership, Payment / Billing, Order / Purchase Issue, Project Support, Refund / Cancellation, Project Feedback
- Feedback: Rate Our Service, Give Feedback, Suggestion / Feature Request, Appreciation / Positive Feedback

## Ticket Metadata
Store the selected category and type with the existing ticket record. Keep the existing ticket ID, opener, guild, channel, status, created_at, and closed_at behavior intact.

## Closure Feedback
When a ticket is closed, offer the opener a private 1-5 star rating and optional written feedback. Record the rating/feedback against the ticket. Do not make the feedback channel public.

## Security
- Ticket rooms remain invisible to @everyone.
- Opener, RupZha bot, and approved staff roles retain access.
- Client restrictions remain enforced for business/client tickets.
- Do not create a channel for a failed or duplicate ticket race.
- Keep one open ticket per member per ticket type.

## Compatibility
Existing open tickets and existing database rows must continue to work. Legacy kinds (support/report/client) remain accepted for old records and slash-command compatibility while the new panel uses the expanded taxonomy.
