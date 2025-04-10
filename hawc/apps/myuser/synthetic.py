import random
from typing import NamedTuple


class UserData(NamedTuple):
    first_name: str
    last_name: str
    username: str
    email: str


# fmt: off
FIRST_NAMES: list[str] = [
    "Alex", "Amelia", "Andrew", "Ava", "Benjamin", "Charlotte", "Chloe", "Chris", "Daniel", "David", "Emily",
    "Emma", "Ethan", "Grace", "Harper", "Isabella", "James", "Jane", "John", "Liam", "Lucas", "Matthew", "Mia",
    "Michael", "Natalie", "Noah", "Olivia", "Sam", "Sophia", "Zoe"
]
LAST_NAMES: list[str] = [
    "Adams", "Allen", "Anderson", "Baker", "Brown", "Carter", "Clark", "Garcia", "Gonzalez", "Hall", "Harris",
    "Jackson", "Johnson", "King", "Lewis", "Martin", "Martinez", "Mitchell", "Nelson", "Robinson", "Rodriguez",
    "Scott", "Smith", "Taylor", "Thomas", "Thompson", "Walker", "White", "Wright", "Young"
]
EMAIL_DOMAINS: list[str] = [
    "anonmail.net", "cloudmail.co", "demo.net", "devemail.net", "dummybox.co", "example.com", "fakemail.co",
    "freemail.org", "hostedmail.com", "instantmail.com", "mail.com", "mailservice.co", "mockmail.com", "myemail.net",
    "onlinemail.org", "placeholder.org", "protonmail.com", "quickmail.net", "randommail.com", "sample.org",
    "samplemail.org", "sandbox.io", "securemail.co", "tempdomain.net", "test.org", "testmail.org", "trialmail.com",
    "virtualmail.com", "webmail.co", "yetanothermail.net"
]
# fmt: on


def _generate_email(first_name: str, last_name: str) -> tuple[str, str]:
    # Generate a realistic username and email address from a first and last name
    domain = random.choice(EMAIL_DOMAINS)  # noqa: S311
    number = random.randint(1, 8096)  # noqa: S311
    username = f"{first_name.lower()}.{last_name.lower()}{number}"
    return username, f"{username}@{domain}"


def generate() -> UserData:
    # Generate synthetic user data
    first_name = random.choice(FIRST_NAMES)  # noqa: S311
    last_name = random.choice(LAST_NAMES)  # noqa: S311
    username, email = _generate_email(first_name, last_name)
    return UserData(first_name=first_name, last_name=last_name, username=username, email=email)
