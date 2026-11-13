import io

def from_txt(uploaded_file, min_pairs: int = 4, max_pairs: int = 100):
    with io.StringIO(uploaded_file.getvalue().decode("utf-8")) as file:
        pair_lines = [line.strip() for line in file]
        if not pair_lines:
            return 
        name = pair_lines[0][:20]
        pairs = []
        for _pair in pair_lines[1:]:
            if "#" not in _pair:
                return 
            pair = _pair.split("#", 1)
            if len(pair) != 2:
                continue
            if pair in pairs:
                continue
            first, second = (pair.strip() for pair in pair)
            pairs.append((first, second))
            if len(pairs) >= max_pairs:
                break

        if len(pairs) < min_pairs:
            return 

        return {"name": name, "pairs": pairs}


def to_txt(deck):
    name = deck["name"]
    pairs = deck["pairs"]
    with io.StringIO() as file:
        file.write(f"{name.title()}\n")
        for label1, label2 in pairs:
            file.write(f"{label1.lower()}#{label2.lower()}\n")

        return file.getvalue()
