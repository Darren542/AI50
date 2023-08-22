import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Dictionary of all pages as keys with odds that next page will be
    # next as values
    model = {} 

    # Get info about the current page
    num_pages = len(corpus)
    page_links = corpus[page]
    num_links = len(page_links)

    # If no links all pages get same odds
    if num_links == 0:
        shared_value = 1 / num_pages
        for key in corpus:
            model.update({ key: shared_value })
        return model

    base_damping = (1 - damping_factor) / (num_pages)
    base_link_chance = damping_factor / num_links
    for possible_page in corpus:
        if possible_page in page_links:
            model.update({possible_page: (base_damping + base_link_chance)})
        else:
            model.update({possible_page: (base_damping)})

    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    corpus_keys = list(corpus.keys())
    current_page = random.choice(corpus_keys)
    sample_results = {}
    for key in corpus_keys:
        sample_results[key] = 0
    for _ in range(n):
        sample_odds = transition_model(corpus, current_page, damping_factor)
        # print(sum(sample_odds.values()))
        roll_result = random.uniform(0, 1)
        current_spot = 0
        for page_key, page_odds in sample_odds.items():
            current_spot += page_odds
            if roll_result <= current_spot:
                sample_results[page_key] += 1
                current_page = page_key
                break
    for key in sample_results:
        sample_results[key] /= n
    return sample_results


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    number_of_pages = len(list(corpus))
    # Make a dict that contains all the pages that link to each page
    link_to_dict = {}
    # Make a dict with the odds of each page
    current_probability = {}
    # fill in starting data
    base_damping = (1 - damping_factor) / number_of_pages

    for key in corpus:
        link_to_dict[key] = set()
        current_probability[key] = 1 / number_of_pages
    for key, value in corpus.items():
        for page in value:
            link_to_dict[page].add(key)

    threshold_change_reach = True
    while threshold_change_reach:
        threshold_change_reach = False
        copy_probability = current_probability.copy()
        for page_key in current_probability:
            sum_parents = 0
            for parent_page in link_to_dict[page_key]:
                sum_parents += current_probability[parent_page] / len(corpus[parent_page])
            new_propability = base_damping + (damping_factor * sum_parents)
            if abs(current_probability[page_key] - new_propability) > 0.001:
                threshold_change_reach = True
            copy_probability[page_key] = new_propability
        current_probability = copy_probability

    normalization_ratio = 1 / sum(current_probability.values())
    for key, value in current_probability.items():
        current_probability[key] = value * normalization_ratio
    return current_probability


if __name__ == "__main__":
    main()
