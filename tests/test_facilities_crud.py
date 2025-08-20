from models.facilities import (
    create_facility,
    get_facility,
    update_facility,
    delete_facility,
)


def test_facility_crud_cycle():
    facility = create_facility("Lab1", facility_type="lab")
    fetched = get_facility(facility.id)
    assert fetched == facility

    updated = update_facility(facility.id, name="LabA", capacity=40)
    assert updated.name == "LabA"
    assert updated.capacity == 40

    assert delete_facility(facility.id) is True
    assert get_facility(facility.id) is None
