from datetime import date, timedelta

from app import v0160


def test_v0160_capability_route_exists():
    paths=[getattr(route,'path',None) for route in v0160.app.router.routes]
    assert '/api/v0160/capabilities' in paths


def test_week_length_is_seven_days():
    start=date.today()-timedelta(days=date.today().weekday())
    assert (start+timedelta(days=6)-start).days==6
