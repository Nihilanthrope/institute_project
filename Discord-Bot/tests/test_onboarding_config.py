from onboarding_config import ONBOARDING_OPTIONS, ONBOARDING_COPY, SELF_ASSIGNABLE_ROLE_NAMES


def test_onboarding_options_are_safe_and_complete():
    assert len(ONBOARDING_OPTIONS) >= 6
    assert all(option["role"] in SELF_ASSIGNABLE_ROLE_NAMES for option in ONBOARDING_OPTIONS)
    assert len({option["role"] for option in ONBOARDING_OPTIONS}) == len(ONBOARDING_OPTIONS)
    assert all(option["label"] and option["description"] for option in ONBOARDING_OPTIONS)


def test_onboarding_copy_tells_joiners_what_to_do():
    assert "role" in ONBOARDING_COPY.lower()
    assert "community" in ONBOARDING_COPY.lower()
    assert "client" in ONBOARDING_COPY.lower()
