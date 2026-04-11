
import re
import argparse
from pathlib import Path

def parse_bib_file(file_path):
    """Parses a .bib file and returns a list of entries."""
    content = Path(file_path).read_text(encoding="utf-8")
    # Split entries. A robust way is to split by the pattern of a new entry starting.
    raw_entries = re.split(r'\n\s*(?=@\w+{)', content)
    return [entry.strip() for entry in raw_entries if entry.strip()]

def extract_year_from_entry(entry_text):
    """Extracts the year from a BibTeX entry string."""
    match = re.search(r'year\s*=\s*[{"]?(\d{4})', entry_text)
    if match:
        return int(match.group(1))
    return 0 # Default to 0 if no year is found, sorting it to the end.

def main():
    parser = argparse.ArgumentParser(description="Merge and sort BibTeX files.")
    parser.add_argument('--inputs', nargs='+', required=True, help="List of input .bib files.")
    parser.add_argument('--output', required=True, help="Path to the output merged .bib file.")
    args = parser.parse_args()

    all_items = []
    for input_file in args.inputs:
        try:
            entries = parse_bib_file(input_file)
            for entry in entries:
                year = extract_year_from_entry(entry)
                # Remove any existing 'selected' field to ensure a clean state
                cleaned_entry = re.sub(r'\s*selected\s*=\s*\{.*?\},?\s*\n', '', entry, flags=re.IGNORECASE)
                all_items.append({'year': year, 'entry': cleaned_entry})
        except FileNotFoundError:
            print(f"Warning: Input file not found: {input_file}")


    # Sort all entries by year, descending
    all_items.sort(key=lambda x: x['year'], reverse=True)

    final_bib_entries = []
    for i, item in enumerate(all_items):
        entry_text = item['entry']
        
        # Find the position of the last closing brace
        last_brace_pos = entry_text.rfind('}')
        if last_brace_pos == -1:
            final_bib_entries.append(entry_text) # Append as is if malformed
            continue

        core_content = entry_text[:last_brace_pos].strip()

        # Ensure the last real field has a comma
        if core_content and not core_content.endswith(','):
            core_content += ','

        if i < 20:
            # Add the 'selected' field for the top 20
            modified_entry = core_content + "\n  selected     = {true}\n}"
        else:
            modified_entry = core_content + "\n}"
        
        # Clean up any double commas that might have been created
        modified_entry = modified_entry.replace(',,', ',')
        final_bib_entries.append(modified_entry)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n\n".join(final_bib_entries), encoding="utf-8")

    print(f"Successfully merged {len(all_items)} entries into {output_path.resolve()}")

if __name__ == "__main__":
    main()
