import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.mines = set()
        self.safe = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safe

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if (cell in self.cells):
            if (self.count == len(self.cells)):
                for cell in self.cells:
                    self.mines.add(cell)
                self.cells.clear()
                self.count = 0
            else:
                self.mines.add(cell)
                self.cells.remove(cell)
                self.count -= 1
                if (self.count == 0):
                    for cell in self.cells:
                        self.safe.add(cell)
                    self.cells.clear()
                    self.count = 0

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if (cell in self.cells):
            if (self.count == 0):
                for cell in self.cells:
                    self.safe.add(cell)
                self.cells.clear()
                self.count = 0
            else:
                self.safe.add(cell)
                self.cells.remove(cell)
                if (self.count == len(self.cells)):
                    for cell in self.cells:
                        self.mines.add(cell)
                    self.cells.clear()
                    self.count = 0


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # mark the cell as a move that has been made
        self.moves_made.add(cell)
        # mark the cell as safe
        self.safes.add(cell)
        for know in self.knowledge:
            know.mark_safe(cell)            
        # add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`
        adjacent_cells = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_cell = (cell[0] + i, cell[1] + j)
                if (new_cell[0] >= 0 and new_cell[1] >=0 and new_cell[0] < self.height and new_cell[1] < self.width and not (i == 0 and j == 0)):
                    adjacent_cells.add((cell[0] + i, cell[1] + j))

        new_knowledge = Sentence(adjacent_cells, count)
        if (count == 0):
            for cell_adj in adjacent_cells:
                self.safes.add(cell_adj)

        for safe_cell in self.safes:
            new_knowledge.mark_safe(safe_cell)
        for mine_cell in self.mines:
            new_knowledge.mark_mine(mine_cell)
        self.knowledge.append(new_knowledge)

        # mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base
        new_knowledge_added = True
        while(new_knowledge_added):
            new_knowledge_added = False
            for know in self.knowledge:
                knows_safe_cells = know.known_safes()
                for known_cell in knows_safe_cells:
                    if known_cell not in self.safes:
                        self.safes.add(known_cell)
                        for sentence in self.knowledge:
                            sentence.mark_safe(known_cell)
                        new_knowledge_added = True
                
                knows_mine_cells = know.known_mines()
                for known_cell in knows_mine_cells:
                    if known_cell not in self.mines:
                        self.mines.add(known_cell)
                        for sentence in self.knowledge:
                            sentence.mark_mine(known_cell)
                        new_knowledge_added = True

            # add any new sentences to the AI's knowledge base
            # if they can be inferred from existing knowledge
            for know1 in self.knowledge:
                for know2 in self.knowledge:
                    if (know1 != know2):
                        # Check if know2 is a subset of know1
                        if (len(know2.cells) > 0 and know2.cells.issubset(know1.cells)):
                            new_set = know1.cells.difference(know2.cells)
                            if len(new_set) > 0:
                                new_mine_count = know1.count - know2.count
                                if new_mine_count < 0:
                                    raise Exception('Error: can\'t have negative count')
                                new_knowledge = Sentence(new_set, new_mine_count)
                                if new_knowledge not in self.knowledge:
                                    self.knowledge.append(new_knowledge)
                                    new_knowledge_added = True

            # Consolidate all Knowledge with empty cell sets into one
            new_knowledge_set = []
            consolitated_safe_cells = set()
            consolitated_mine_cells = set()
            for know in self.knowledge:
                if len(know.cells) > 0:
                    new_knowledge_set.append(know)
                else:
                    consolitated_safe_cells.update(know.safe)
                    consolitated_mine_cells.update(know.mines)
            if len(consolitated_safe_cells) > 0:
                consoliated_safe_knowledge = Sentence(consolitated_safe_cells, 0)
                consoliated_safe_knowledge.mark_safe(consolitated_safe_cells.pop())
                new_knowledge_set.append(consoliated_safe_knowledge)
            if len(consolitated_mine_cells) > 0:
                consoliated_mines_knowledge = Sentence(consolitated_mine_cells, len(consolitated_mine_cells))
                consoliated_mines_knowledge.mark_mine(consolitated_mine_cells.pop())
                new_knowledge_set.append(consoliated_mines_knowledge)
            self.knowledge = new_knowledge_set
            


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        unchoosen_moves = self.safes.difference(self.moves_made)
        if (len(unchoosen_moves) > 0):
            return unchoosen_moves.pop()
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_possible_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                all_possible_moves.add((i, j))
        cant_be_taken = self.moves_made.union(self.mines)
        remaining_moves = all_possible_moves.difference(cant_be_taken)
        if (len(remaining_moves) > 0):
            return remaining_moves.pop()
        return None
