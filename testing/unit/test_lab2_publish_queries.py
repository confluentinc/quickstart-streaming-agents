"""Exercise the publisher's public CLI argument forms without cloud access."""

import pytest

from scripts.lab2_publish_queries import parse_args


@pytest.mark.parametrize(
    ("argv", "provider", "question"),
    [
        ([], None, None),
        (
            ["How do window functions work in Flink SQL?"],
            None,
            "How do window functions work in Flink SQL?",
        ),
        (["aws"], "aws", None),
        (["azure"], "azure", None),
        (["aws", "What is watermarking?"], "aws", "What is watermarking?"),
        (
            ["azure", "How do I join tables?", "--verbose"],
            "azure",
            "How do I join tables?",
        ),
        (
            ["--topic", "questions", "How do windows work?"],
            None,
            "How do windows work?",
        ),
    ],
)
def test_publisher_argument_forms(argv, provider, question):
    args = parse_args(argv)
    assert (args.cloud_provider, args.query) == (provider, question)
    assert args.topic == ("questions" if "--topic" in argv else "queries")
    assert args.verbose == ("--verbose" in argv)


def test_unquoted_question_has_actionable_error(capsys):
    with pytest.raises(SystemExit) as failure:
        parse_args(["How", "do", "windows", "work?"])
    assert failure.value.code == 2
    assert "one quoted question" in capsys.readouterr().err
