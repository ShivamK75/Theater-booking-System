from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n") if f.readable() else []

setup(
    name="theatre_booking",
    version="0.0.1",
    description="Theatre Ticket Booking System app for Frappe",
    author="Shivam",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
