import pandas as pd
from symspellpy import SymSpell, Verbosity
import pkg_resources
import re

sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt"
)
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

# Commonly used address terms mapping to standard terms
ADDRESS_TERMS = {
    'street': ['st', 'street', 'str'],
    'avenue': ['ave', 'avenue', 'av'],
    'drive': ['dr', 'drive', 'drv'],
    'road': ['rd', 'road'],
    'lane': ['ln', 'lane'],
    'circle': ['cir', 'circle', 'crcl'],
    'boulevard': ['blvd', 'boulevard', 'boul'],
    'place': ['pl', 'place'],
    'court': ['ct', 'court', 'crt'],
    'square': ['sq', 'square'],
    'highway': ['hwy', 'highway', 'hiway'],
    'parkway': ['pkwy', 'parkway'],
    'expressway': ['expy', 'expressway'],
    'plaza': ['plz', 'plaza'],
    'trail': ['tr', 'trail', 'trl'],
    'way': ['wy', 'way'],
    'alley': ['aly', 'alley'],
    'terrace': ['ter', 'terrace'],
    'pike': ['pk', 'pike'],
    'grove': ['grv', 'grove'],
    'ridge': ['rdg', 'ridge'],
    'north': ['n', 'no', 'nth'],
    'south': ['s', 'so', 'sth'],
    'east': ['e', 'ea'],
    'west': ['w', 'we'],
    'northeast': ['ne'],
    'northwest': ['nw'],
    'southeast': ['se'],
    'southwest': ['sw']
}

# All US States mapping to their abbreviations
US_STATES = {
    'AL': ['alabama', 'al'],
    'AK': ['alaska', 'ak'],
    'AZ': ['arizona', 'az'],
    'AR': ['arkansas', 'ar'],
    'CA': ['california', 'ca', 'calif'],
    'CO': ['colorado', 'co'],
    'CT': ['connecticut', 'ct', 'conn'],
    'DE': ['delaware', 'de'],
    'FL': ['florida', 'fl', 'fla'],
    'GA': ['georgia', 'ga'],
    'HI': ['hawaii', 'hi'],
    'ID': ['idaho', 'id'],
    'IL': ['illinois', 'il'],
    'IN': ['indiana', 'in'],
    'IA': ['iowa', 'ia'],
    'KS': ['kansas', 'ks'],
    'KY': ['kentucky', 'ky'],
    'LA': ['louisiana', 'la'],
    'ME': ['maine', 'me'],
    'MD': ['maryland', 'md'],
    'MA': ['massachusetts', 'ma', 'mass'],
    'MI': ['michigan', 'mi', 'mich'],
    'MN': ['minnesota', 'mn', 'minn'],
    'MS': ['mississippi', 'ms'],
    'MO': ['missouri', 'mo'],
    'MT': ['montana', 'mt'],
    'NE': ['nebraska', 'ne', 'nebr'],
    'NV': ['nevada', 'nv'],
    'NH': ['new hampshire', 'nh'],
    'NJ': ['new jersey', 'nj'],
    'NM': ['new mexico', 'nm'],
    'NY': ['new york', 'ny'],
    'NC': ['north carolina', 'nc'],
    'ND': ['north dakota', 'nd'],
    'OH': ['ohio', 'oh'],
    'OK': ['oklahoma', 'ok'],
    'OR': ['oregon', 'or'],
    'PA': ['pennsylvania', 'pa'],
    'RI': ['rhode island', 'ri'],
    'SC': ['south carolina', 'sc'],
    'SD': ['south dakota', 'sd'],
    'TN': ['tennessee', 'tn', 'tenn'],
    'TX': ['texas', 'tx'],
    'UT': ['utah', 'ut'],
    'VT': ['vermont', 'vt'],
    'VA': ['virginia', 'va'],
    'WA': ['washington', 'wa', 'wash'],
    'WV': ['west virginia', 'wv'],
    'WI': ['wisconsin', 'wi', 'wis', 'wisc'],
    'WY': ['wyoming', 'wy'],
    'DC': ['district of columbia', 'dc'],
    'PR': ['puerto rico', 'pr'],
    'VI': ['virgin islands', 'vi'],
    'GU': ['guam', 'gu'],
    'MP': ['northern mariana islands', 'mp'],
    'AS': ['american samoa', 'as']
}

# Function to standardize zip codes to 5 digit standard
def standardize_zip(zip_code):

    if pd.isna(zip_code) or zip_code == '':
        return None
    zip_str = re.sub(r'\D', '', str(zip_code))
    if len(zip_str) > 5:
        zip_str = zip_str[:5]
    return zip_str.zfill(5)


# Function to standardize state abbreviations
def standardize_state(state):
    if pd.isna(state) or state == '':
        return None
    
    state = state.lower().strip()
    if state.upper() in US_STATES.keys():
        return state.upper()

    for code, variations in US_STATES.items():
        if state in variations:
            return code
        
    return None

# Function to clean and standardize street address
def clean_street_address(address):
    if pd.isna(address) or address == '':
        return None
        
    address = address.lower().strip()
    address = re.sub(r'[^\w\s#-]', '', address)
    words = address.split()
    cleaned_words = []
    
    for word in words:
        if word.isdigit() or '#' in word:
            cleaned_words.append(word)
            continue

        term_found = False
        for standard, variations in ADDRESS_TERMS.items():
            if word in variations:
                cleaned_words.append(standard)
                term_found = True
                break
        
        if not term_found:
            suggestions = sym_spell.lookup(
                word,
                Verbosity.CLOSEST,
                max_edit_distance=2
            )
            if suggestions:
                cleaned_words.append(suggestions[0].term)
            else:
                cleaned_words.append(word)

    cleaned_address = ' '.join(cleaned_words)
    return cleaned_address.title()


# Function to clean and standardize city name
def clean_city(city):
    if pd.isna(city) or city == '':
        return None

    city = city.lower().strip()
    city = re.sub(r'[^\w\s]', '', city)
    suggestions = sym_spell.lookup(
        city,
        Verbosity.CLOSEST,
        max_edit_distance=2
    )
    
    if suggestions:
        city = suggestions[0].term
        
    return city.title()

# Apply all cleaning functions to a copy of the dataset
def clean_addresses(df):
    cleaned_df = df.copy()
    cleaned_df['street'] = cleaned_df['street'].apply(clean_street_address)
    cleaned_df['city'] = cleaned_df['city'].apply(clean_city)
    cleaned_df['state'] = cleaned_df['state'].apply(standardize_state)
    cleaned_df['zip'] = cleaned_df['zip'].apply(standardize_zip)
    return cleaned_df


# Function to remove duplicate addresses
def remove_duplicates(df):
    duplicates = df[df.duplicated(subset=['street', 'city', 'state', 'zip'], keep=False)]
    if not duplicates.empty:
        print("\nDuplicate addresses found:")
        print(duplicates[['street', 'city', 'state', 'zip']])
        print(f"\nTotal duplicates found: {len(duplicates)}")
    before_dedup = len(df)
    df = df.drop_duplicates(subset=['street', 'city', 'state', 'zip'], keep='first')
    after_dedup = len(df)
    print(f"\nRemoved {before_dedup - after_dedup} duplicate addresses.")
    return df

def process_file(input_file, output_file):
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{input_file}' was not found. Please check the file path.")
    except pd.errors.EmptyDataError:
        raise ValueError(f"The file '{input_file}' is empty.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file '{input_file}': {str(e)}")
    cleaned_df = clean_addresses(df)

    # Duplicate removal applied after cleaning and standardization to avoid missing duplicates
    cleaned_df = remove_duplicates(cleaned_df)

    cleaned_df.to_csv(output_file, index=False)
    return cleaned_df

cleaned_data = process_file('list_of_real_usa_addresses.csv', 'cleaned_addresses.csv')