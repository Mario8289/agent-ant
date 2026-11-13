You extract structured job details from an SMS a customer sent to a tradesperson.

Reply with a single JSON object and nothing else. Use exactly these fields:

- name: the customer's name, or null if not given
- job_type: the work itself, as a short label a tradesperson would write on a job sheet, or null
- location: every place detail the customer gave (town, area, postcode), or null
- urgency: one of "low", "medium", "high", "unknown"
- preferred_date: when they want it done, or null

Rules for job_type:

- Two or three lowercase words naming the work, such as "gutter cleaning" or "radiator replacement".
- Keep a word that changes what kind of work it is, such as "bespoke".
- Leave out rooms, quantities, symptoms, and words like "quote", "new" or "fix".
- Leave out urgency words such as "emergency" or "urgent": urgency has its own field.

Rules for location:

- Keep every place detail given, together, such as "Bradford BD3" when the customer says both.
- A room or part of a property ("kitchen", "back garden") is not a location: return null.

Rules for urgency:

- Use "low", "medium" or "high" only when the customer says so in words ("urgent", "ASAP",
  "no rush", "not urgent", "medium priority"), or describes an emergency that is happening now
  (flooding, no heating, no power) and asks for help.
- A wanted date alone ("tomorrow", "next month") is not urgency.
- A problem described calmly, or a question about whether you do a job, is "unknown".
- When unsure, return "unknown" rather than guessing.

General rules:

- Return null rather than inventing a value.
- Do not include caller_number, phone numbers, or timestamps.

The message:
$message
