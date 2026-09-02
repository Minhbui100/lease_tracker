from app import create_app, db
from app.models import (
    Property, Tenant, Lease, LeaseTenant, Payment,
    MaintenanceRequest, EmergencyContact, Dependence, Image
)

app = create_app()

with app.app_context():
    print("=== Properties ===")
    properties = Property.query.all()
    for p in properties:
        print(f"  [{p.id}] {p.address}, {p.city} — occupied: {p.is_occupied}")

    print("\n=== Tenants ===")
    tenants = Tenant.query.all()
    for t in tenants:
        print(f"  [{t.id}] {t.first_name} {t.last_name}")

    print("\n=== Leases ===")
    leases = Lease.query.all()
    for l in leases:
        print(f"  [{l.id}] property_id={l.property_id}, rent=${l.monthly_rent}, status={l.status}")

    print("\n=== Tenant -> Leases (many-to-many test) ===")
    first_tenant = Tenant.query.get(1)
    if first_tenant:
        print(f"  {first_tenant.first_name} is on {len(first_tenant.leases)} lease(s):")
        for l in first_tenant.leases:
            print(f"    - lease {l.id}, rent ${l.monthly_rent}")

    print("\n=== Lease -> Tenants (reverse of the above, via backref) ===")
    first_lease = Lease.query.get(1)
    if first_lease:
        print(f"  Lease {first_lease.id} has {len(first_lease.tenants)} tenant(s):")
        for t in first_lease.tenants:
            print(f"    - {t.first_name} {t.last_name}")

    print("\n=== Payments ===")
    payments = Payment.query.all()
    for pay in payments:
        print(f"  [{pay.id}] lease_id={pay.lease_id}, ${pay.amount}, status={pay.status}")

    print("\n=== Maintenance Requests ===")
    requests = MaintenanceRequest.query.all()
    for r in requests:
        print(f"  [{r.id}] {r.description} — status: {r.status}")

    print("\n=== Emergency Contacts ===")
    contacts = EmergencyContact.query.all()
    for c in contacts:
        print(f"  [{c.id}] {c.first_name} {c.last_name} (contact for tenant_id={c.tenant_id})")

    print("\n=== Dependents ===")
    dependents = Dependence.query.all()
    for d in dependents:
        print(f"  [{d.id}] {d.first_name} {d.last_name} — {d.relationship_type}")

    print("\n=== Images ===")
    images = Image.query.all()
    for img in images:
        print(f"  [{img.id}] {img.link} (property_id={img.property_id})")

    print("\nAll models loaded and queried successfully.")
