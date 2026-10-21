# Lease Tracker

A web app for managing rental properties. Staff can keep track of properties, tenants, leases, rent payments, and maintenance requests in one place, and see how much money each property is making or costing.

Built with Flask and PostgreSQL.

## What it does

- **Staff login.** Every page requires signing in. Passwords are stored hashed.
- **Properties.** Add, edit, and delete properties. Each property has a detail page with its leases, maintenance history, photos, and cash flow.
- **Photos.** Upload and delete images for a property straight from your computer.
- **Tenants.** Add, edit, and delete tenants.
- **Leases.** A lease links one property to one or more co-tenants.
  - Status comes from the dates: a lease is `expired` once its end date has passed, otherwise `active`.
  - Ending a lease early goes through a **Terminate** button that asks for a reason.
  - A property is marked occupied whenever it has an active lease.
- **Payments.** Track rent and deposits, with a category, a pay type (check, cash, Zelle, bank transfer), and a memo.
- **Maintenance requests.** Log issues for a property, note whether a tenant or staff reported it, track them from open to resolved, and record material cost, labor cost, and who paid.
- **Dashboard.** Counts of active leases, late and pending payments, and open maintenance tickets.
- **Cash flow per property.** Cash in is paid rent and deposits. Cash out is owner-paid maintenance plus expenses you enter (down payment, closing costs, mortgage, HOA, property tax, insurance, utilities, management fee, remodel, legal, other). A summary table shows each category and the balance.
- **Form validation.** Forms are checked on the server and show readable error messages.

## Automatic jobs

Three scheduled jobs run inside the app (APScheduler):

| Job | When | What it does |
|---|---|---|
| Expire leases | Every night at midnight | Marks active leases as expired once the end date has passed |
| Flag late payments | Every night at midnight | Marks pending payments as late once the due date has passed |
| Generate rent | 1st of each month, midnight | Creates a pending rent payment for every active lease |

These only run while the app is running. If the server is off at midnight, that night's run is skipped.

## Tech stack

Python, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, APScheduler, PostgreSQL, Jinja templates, HTML/CSS.

## Getting started

You need Python 3.9 or newer and PostgreSQL.

1. **Clone the repo and set up a virtual environment**

   ```bash
   git clone https://github.com/Minhbui100/lease_tracker.git
   cd lease_tracker
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create the database**

   ```bash
   createdb lease_tracker
   ```

3. **Add a `.env` file** in the project root:

   ```
   DATABASE_URL=postgresql://localhost/lease_tracker
   SECRET_KEY=replace-this-with-a-long-random-string
   FLASK_APP=run.py
   ```

   You can generate a secret key with
   `python3 -c "import secrets; print(secrets.token_hex(32))"`.
   Never commit this file.

4. **Create the tables**

   ```bash
   flask db upgrade
   ```

5. **Create your first staff user.** Open `create_staff_user.py`, set your own username and password, then run:

   ```bash
   python3 create_staff_user.py
   ```

6. **(Optional) Load sample data**

   ```bash
   psql -d lease_tracker -f seed_data.sql
   ```

7. **Run the app**

   ```bash
   python3 run.py
   ```

   Open http://127.0.0.1:5000/login and sign in.

## Project layout

```
app/
  __init__.py        app factory and scheduled jobs
  models.py          database models
  validation.py      shared form validation
  auth/              login and logout
  dashboard/         dashboard page
  properties/        properties, photos, expenses, cash flow
  tenants/           tenants
  leases/            leases and termination
  payments/          payments
  maintenance/       maintenance requests
  templates/         HTML templates
  static/uploads/    uploaded property photos (not committed)
migrations/          database migrations
config.py            settings read from .env
run.py               entry point
```

## Database changes

Schema changes go through Flask-Migrate:

```bash
flask db migrate -m "describe the change"
flask db upgrade
```

Always open the generated file in `migrations/versions/` before upgrading. Alembic reads a column rename as a drop plus an add, which would delete data, and it does not detect changes to `CHECK` constraints, so those need a hand-written migration.

## Known limitations

- Each property is leased as a whole. There is no separate unit table, so a multi-family building can only have one lease at a time.
- The `emergency_contact` and `dependence` tables exist, but there are no pages for them yet.
- Cash flow is an all-time total. Payments store a due date but not the date they were actually paid, so there is no monthly or yearly view.
- Forms do not have CSRF protection yet.
- Photos are saved to the local disk, so they are not shared across servers.
- The scheduled jobs depend on the app staying up. For a real deployment, run them with a proper scheduler.
