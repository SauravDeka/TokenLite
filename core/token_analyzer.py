import tiktoken


TOKENIZER_NAME = "o200k_base"


def get_tokenizer():
    return tiktoken.get_encoding(
        TOKENIZER_NAME
    )


def count_tokens(text):
    text = text or ""

    tokenizer = get_tokenizer()

    return len(
        tokenizer.encode(
            text
        )
    )


def analyze_text(text):
    text = text or ""

    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(
            text.splitlines()
        ),
        "tokens": count_tokens(
            text
        ),
    }


def calculate_token_savings(
    original_tokens,
    optimized_tokens,
):
    original_tokens = int(
        original_tokens or 0
    )

    optimized_tokens = int(
        optimized_tokens or 0
    )

    saved = max(
        original_tokens - optimized_tokens,
        0,
    )

    if original_tokens == 0:
        reduction = 0.0
    else:
        reduction = (
            saved / original_tokens
        ) * 100

    return {
        "tokens_saved": saved,
        "reduction_percent": reduction,
    }