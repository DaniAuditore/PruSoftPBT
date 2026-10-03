from hypothesis import strategies as st

# A non-whitespace anchor guarantees a valid stripped title without filtering.
TITLES = st.builds(
    lambda prefix, suffix: prefix + "B" + suffix,
    st.text(max_size=59),
    st.text(max_size=60),
)
PAGES = st.integers(min_value=1, max_value=10_000)
FIELDS = st.tuples(TITLES, PAGES)
BOOK_LISTS = st.lists(FIELDS, min_size=1, max_size=12)
INVALID_TITLES = st.one_of(
    st.none(),
    st.integers(),
    st.lists(st.sampled_from([" ", "\t", "\n", "\u2003"]), max_size=20).map("".join),
    st.integers(min_value=121, max_value=160).map(lambda size: "X" * size),
)
INVALID_PAGES = st.one_of(
    st.none(),
    st.booleans(),
    st.text(max_size=10),
    st.floats(),
    st.integers(max_value=0),
    st.integers(min_value=10_001),
)
INVALID_FIELDS = st.one_of(
    st.tuples(INVALID_TITLES, PAGES), st.tuples(TITLES, INVALID_PAGES)
)
INVALID_IDS = st.one_of(
    st.none(),
    st.booleans(),
    st.text(max_size=10),
    st.floats(),
    st.integers(max_value=0),
)
