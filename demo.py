"""Run with the virtual environment's Python executable: python demo.py."""

from catalog import Catalog


def main() -> None:
    catalog = Catalog()
    original = catalog.create("  Property-Based Testing  ", 240)
    print("Created:", original)
    assert catalog.read(original.id) == original
    print("Read:", catalog.read(original.id))
    updated = catalog.update(original.id, "Property-Based Testing, revised", 260)
    assert updated.id == original.id and original.pages == 240
    print("Updated:", updated)
    assert catalog.delete(original.id) == updated
    print("Deleted:", original.id)
    try:
        catalog.read(original.id)
    except KeyError:
        print("Deleted ID is missing as expected.")
    else:
        raise AssertionError("Deleted book is still readable")
    later = catalog.create("A New Book", 100)
    assert later.id > original.id
    print("New ID (not reused):", later.id)
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
