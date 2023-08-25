import sys
from typing import Dict

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword : Crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        # #TODO Temp for testing
        # for var1 in self.domains:
        #     for var2 in self.domains:
        #         if var1 != var2:
        #             self.revise(var1, var2)
        #         else:
        #             continue
        #     break
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlaps = self.crossword.overlaps[x, y]
        # print('x', x)
        # print('y', y)
        # print('overlaps', overlaps)
        revision_made = False
        if overlaps is None:
            return False
        for word in self.domains[x].copy():
            # print(word)
            # print(word[overlaps[0]])
            letter = word[overlaps[0]]
            possible_word = any(y_word[overlaps[1]] == letter for y_word in self.domains[y])
            if not possible_word:
                self.domains[x].remove(word)
                revision_made = True
        # print('remaining words')
        # for word in self.domains[x]:
        #     print(word)
        return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        arc_queue = arcs
        if arc_queue is None:
            arc_queue = []
            for x in self.domains:
                for y in self.domains:
                    if x is not y:
                        arc_queue.append(tuple((x, y)))

        # print('arc queue', arc_queue)
        while len(arc_queue) != 0:
            arc = arc_queue.pop()
            # print('arc', arc)
            revise_result = self.revise(arc[0], arc[1])
            if revise_result:
                if len(self.domains[arc[0]]) == 0:
                    return False
                neighbors = self.crossword.neighbors(arc[0])
                # print('neightbors', neighbors)
                for neigh in neighbors:
                    arc_queue.append(tuple((arc[0], neigh)))

        # print(self.domains)

    def assignment_complete(self, assignment: Dict[Variable, str]):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var in assignment.keys():
                if not assignment[var]:
                    return False
            else:
                return False
        return True

    def consistent(self, assignment: Dict[Variable, str]):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        all_words = []
        for var, word in assignment.items():
            # No duplicate words
            if word not in all_words:
                all_words.append(word)
            else:
                return False
            # Word is right length
            if not var.length == len(word):
                return False
            # Check Neighbor
            neighbors = self.crossword.neighbors(var)
            for neigh in neighbors:
                # does neighbor have word assigned?
                if neigh in assignment.keys():
                    # Do the overlapping letters match up?
                    neigh_word = assignment[neigh]
                    overlaps = self.crossword.overlaps[var, neigh]
                    if overlaps:
                        if neigh_word[overlaps[1]] != word[overlaps[0]]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Get vars unassigned neighbors
        neighbors = list(filter(lambda v: v not in assignment.keys(), self.crossword.neighbors(var)))
        if len(neighbors) == 0:
            return self.domains[var]

        def sort_function(word: str):
            total_removed = 0
            for neigh in neighbors:
                overlap = self.crossword.overlaps[var, neigh]
                total_removed += self.overlap_count(word[overlap[0]], overlap[1], neigh)
            return total_removed

        copy_words = self.domains[var].copy()
        copy_words = sorted(self.domains[var], key=sort_function)

        return copy_words
    
    def overlap_count(self, char, spot, var):
        """
        Count how many words this character at this spot would remove from a variables domain
        """
        current_amount = len(self.domains[var])
        after_filter = len(list(filter(lambda word: word[spot] == char, self.domains[var])))
        return current_amount - after_filter

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        min_remaining_values = 1e6
        current_highest_degree = 0
        current_var = None
        for var, words in self.domains.items():
            if var not in assignment.keys():
                remaining_values = len(words)
                current_degree = len(self.crossword.neighbors(var))
                if remaining_values < min_remaining_values or (remaining_values == min_remaining_values and current_degree > current_highest_degree):
                    current_var = var

        return current_var

    def backtrack(self, assignment: Dict[Variable, str]):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        new_var = self.select_unassigned_variable(assignment)
        ordered_word_list = self.order_domain_values(new_var, assignment)
        for word in ordered_word_list:
            assignment.update({new_var: word})
            is_consistant = self.consistent(assignment)
            if is_consistant:
                result = self.backtrack(assignment)
                if result is not None and self.consistent(result):
                    return result
            del assignment[new_var]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
