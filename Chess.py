#Matthew Jordan and Paul Crowley
#Chess, a "simple" chess game with basic features
#2024-12-05 first draft outlining class and GUI - created the background (black and white checkerboard)
#                                                 and played around with images although didn't implement
#2024-12-12 FINALLY got the pieces to move correctly STILL NEED TO implement can_move methods
#2024-12-16 FINAL adjustments for presentation
#TODO: get the clock working, make win conditions (check and checkmate)
#Sources:
#       https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QGridLayout.html
#       https://doc.qt.io/qtforpython-6/PySide6/QtCore/QTimer.html
#       https://www.pythonguis.com/tutorials/pyside6-dialogs/
#
# HOW TO USE: install PySide6


from PySide6.QtWidgets import (QApplication, QMainWindow,
                               QPushButton, QGridLayout,
                               QWidget, QLabel, QDialog,
                               QDialogButtonBox, QVBoxLayout)
from PySide6.QtCore import QTimer 

    

class Pawn:
    def __init__(self, color='none'):
        self.color = color
        self.point = 1
        self.icon = '♟' if self.color == 'black' else '♙'

    def __str__(self):
        return 'Pawn'

    def __repr__(self):
        return f"Pawn('{self.color}')"

    def can_move(self, start_row, start_col, end_row, end_col, board):
        '''TESTING THE MOVES (manual): O means valid, X means not valid 
            format: White Pawn moves from 0,0 to 1,0 == WP(0,0) -> E(1,0)
        WP(6,3) -> E(4,3)  O
        BP(1,4) -> E(3,4)  O
        WP(4,3) -> BP(3,4) O # white captures black
        BP(1,3) -> E(3,3)  O
        WP(3,4) -> E(2,3)  X # en passant -not implemented
        WP(6,4) -> E(4,4)  O
        BP(3,3) -> WP(4,4) O # black captures white
        PAWN PROMOTION NOT IMPLEMENTED
        '''
        # Determines the direction of the color (White would go up +1, black down -1)
        direction = 1 if self.color == 'black' else -1 
        # Checks if pawn is moving straight
        if start_col == end_col:  
            # Checks for empty square to move forward up ONE
            if isinstance(board[end_row][end_col], Empty): # If the destination is empty
                if end_row - start_row == direction: # Move Forward one step/square space
                    return True
                # Checks if it can move 2 empty square spaces to on the FIRST move
                if (self.color == 'white' and start_row == 6 \
                    or self.color == 'black' and start_row == 1)\
                    and end_row - start_row == 2 * direction:
                    # Makes sure the square in between is already empty
                    return isinstance(board[start_row + direction][start_col], Empty)
        # Check to see if it can capture one space diagonally 
        elif abs(end_col - start_col) == 1 and end_row - start_row == direction: 
            # Makes sure that the piece is an opponents piece, not the same color
            return board[end_row][end_col].color != self.color and not isinstance(board[end_row][end_col], Empty)
        # If nothing is valid (Moving to the side, more than 2 spaces at the beginning, etc.), returns as an invalid move
        return False



class Rook:
    def __init__(self, color='none'):
        self.color = color
        self.point = 5
        self.icon = '♜' if self.color == 'black' else '♖'

    def __str__(self):
        return 'Rook'

    def __repr__(self):
        return f"Rook('{self.color}')"

    def can_move(self, start_row, start_col, end_row, end_col, board):
        '''TESTING THE MOVES (manual): O means valid, X means not valid 
            format: White Rook moves from 0,0 to 1,0 == WR(0,0) -> E(1,0)
        WP(6,0) -> E(4,0)  O # move pawn out of way
        BP(1,7) -> E(3,7)  O # move pawn out of way
        WR(7,0) -> E(3,0)  X # cannot through pieces
        WR(7,0) -> E(5,0)  O
        BR(0,7) -> E(2,7)  O
        WR(5,0) -> E(5,3)  O
        BR(2,7) -> E(2,6)  O
        WR(5,3) -> BP(1,3) O # captures black
        BR(2,6) -> WP(6,6) O # captures white
        CASTLING NOT IMPLEMENTED
        '''
        # Checks to see if it can move horizontally 
        if start_row == end_row:  
            step = 1 if end_col > start_col else -1 # Determines direction 
            # Loops over the squares from the start col to the end to see if theres any obstructions
            for col in range(start_col + step, end_col, step):
                if not isinstance(board[start_row][col], Empty): 
                    return False # Blocked from moving
                # Stop the Rook from friendly firing
            return board[end_row][end_col].color != self.color # Executes move if everything is valid
        
        # Checks if the Rook can move vertically
        elif start_col == end_col:  # Vertical move
            step = 1 if end_row > start_row else -1
            # Loops over the squares from the start col to the end to see if theres any obstructions
            for row in range(start_row + step, end_row, step):
                if not isinstance(board[row][start_col], Empty): # Blocked
                    return False # Blocked from Moving
            # Stop the Rook from friendly firing...again
            return board[end_row][end_col].color != self.color # Executes move if everything is valid
        # If it cannot move either horizontally or vertically, the move becomes invalid
        return False


class Knight:

    def __init__(self, color='none'):
        self.color = color
        self.point = 3
        self.icon = '♞' if self.color == 'black' else '♘'

    def __str__(self):
        return 'Knight'

    def __repr__(self):
        return f"Knight('{self.color}')"

    def can_move(self, start_row, start_col, end_row, end_col, board):
        '''TESTING THE MOVES (manual): O means valid, X means not valid 
            format: White Rook moves from 0,0 to 1,0 == WR(0,0) -> E(1,0)
        WKn(7,1) -> E(5,2)  O
        BKn(0,6) -> E(2,5)  O
        WKn(5,2) -> E(3,3)  O
        BKn(2,5) -> WKn(3,3) O # captures white
        WKn(7,6) -> E(5,6)  X # invalid move location
        WKn(7,6) -> E(5,5)  O
        BP(1,4) -> E(3,4)  O
        WKn(5,5) -> E(3,4)  O # captures black
        '''
        # Calculates the absolute difference between rows and columns
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        # Returns an L-shape pattern move
        return (row_diff, col_diff) in [(2, 1), (1, 2)] and board[end_row][end_col].color != self.color


class Bishop:
    def __init__(self, color='none'):
        self.color = color
        self.point = 3
        self.icon = '♝' if self.color == 'black' else '♗'

    def __str__(self):
        return 'Bishop'

    def __repr__(self):
        return f"Bishop('{self.color}')"

    def can_move(self, start_row, start_col, end_row, end_col, board):
        '''TESTING THE MOVES (manual): O means valid, X means not valid 
            format: White Rook moves from 0,0 to 1,0 == WR(0,0) -> E(1,0)
        WP(6,3) -> E(4,3)  O
        BP(1,3) -> E(3,3)  O
        WB(7,2) -> E(3,6)  O
        BB(0,2) -> E(4,6)  O
        WB(3,6) -> BB(4,6) X # invalid move
        WB(3,6) -> BP(1,4) O # capture black
        BB(4,6) -> WP(6,4) O # capture white
        WB(1,4) -> BB(0,5) O # capture another black
        '''
        # Checks if it's able to move diagonally (equal row and column difference)
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        if row_diff == col_diff:  # Diagonal move
            # Determines the direction of the move for rows and columns
            step_row = 1 if end_row > start_row else -1
            step_col = 1 if end_col > start_col else -1
            # Check for obstructions in its pathway when moving
            for i in range(1, row_diff):
                if not isinstance(board[start_row + i * step_row][start_col + i * step_col], Empty):
                    return False # Blocked move; becomes invalid
            # Stop the Bishop from friendly firing
            return board[end_row][end_col].color != self.color # Executes move if everything is valid
        return False


class Queen:
    def __init__(self, color='none'):
        self.color = color
        self.point = 9
        self.icon = '♛' if self.color == 'black' else '♕'

    def __str__(self):
        return 'Queen'

    def __repr__(self):
        return f"Queen('{self.color}')"

    def can_move(self, start_row, start_col, end_row, end_col, board):
        '''TESTING THE MOVES (manual): O means valid, X means not valid 
            format: White Rook moves from 0,0 to 1,0 == WR(0,0) -> E(1,0)
        WP(6,4) -> E(5,4)  O
        BP(1,3) -> E(3,3)  O
        WQ(7,3) -> E(4,6)  O # bishop moveset
        BQ(0,3) -> E(2,3)  O # rook moveset
        WQ(4,6) -> BP(1,6) O # rook moveset capture black
        BQ(2,3) -> WP(6,7) O # bishop moveset capture white
        WQ(1,6) -> E(3,5)  X # knight moveset not valid
        WQ(1,6) -> E(1,3)  X # cannot move thru pieces
        '''
        # Combines the Rook's and Bishop's moves
        return Rook(self.color).can_move(start_row, start_col, end_row, end_col, board) or \
               Bishop(self.color).can_move(start_row, start_col, end_row, end_col, board)


class King:
    def __init__(self, color='none'):
        self.point = 0
        self.color = color
        self.icon = '♚' if self.color == 'black' else '♔'

    def __str__(self):
        return 'King'

    def __repr__(self):
        return f"King('{self.color}')"

    def can_move(self, start_row, start_col, end_row, end_col, board):
        '''TESTING THE MOVES (manual): O means valid, X means not valid 
            format: White Rook moves from 0,0 to 1,0 == WR(0,0) -> E(1,0)
        WP(6,4) -> E(4,4)  O
        BP(1,4) -> E(3,4)  O
        WKi(7,4) -> E(6,4) O
        BQ(0,3) -> E(3,6)  O
        WKi(6,4) -> E(5,4) O # should NOT be legal: moving into check
        BKi(0,4) -> E(0,3) O
        WKi(5,4) -> E(5,3) O # should NOT be legal: moving out of check
        CASTLING NOT IMPLEMENTED
        '''
        # Calculates the absolute difference between rows and columns for the King to move
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        # The move is valid if King moves only 1 square in any direction thats empty
        return max(row_diff, col_diff) == 1 and board[end_row][end_col].color != self.color


class Empty:
    def __init__(self):
        self.point = 0
        self.color = None
        self.icon = ''

    def __str__(self):
        return 'Empty'

    def __repr__(self):
        return 'Empty()'

    def can_move(self, *args):
        # Empty square cannot move...obviously
        return False


class Chess(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Chess Game')
        self.turn = 'white'

        self.grid = QGridLayout()
        self.initialize_pieces()
        self.initialize_buttons()

        self.row = None
        self.col = None

        # Set the time for each player
        self.timer_time = 60
        self.black_time = self.timer_time
        self.white_time = self.timer_time

        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer_running = False  # Flag to manage timer state

        # Score label stuff
        self.white_score = 0
        self.black_score = 0
        self.white_icons = ''
        self.black_icons = ''

        self.setup_board()
        self.displays()

        panel = QWidget()
        panel.setLayout(self.grid)
        self.setCentralWidget(panel)

    

    
    def initialize_pieces(self):
        '''Creates the 2d list of chess pieces (the internal state of the game)'''
        self.pieces = [[Rook('black'),Knight('black'), Bishop('black'), Queen('black'), King('black'), Bishop('black'), Knight('black'), Rook('black')],\
                        [Pawn('black'), Pawn('black'), Pawn('black'), Pawn('black'), Pawn('black'), Pawn('black'), Pawn('black'), Pawn('black')],\
                        [Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty()],\
                        [Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty()],\
                        [Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty()],\
                        [Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty()],\
                        [Pawn('white'), Pawn('white'), Pawn('white'), Pawn('white'), Pawn('white'), Pawn('white'), Pawn('white'), Pawn('white')],\
                        [Rook('white'),Knight('white'), Bishop('white'), Queen('white'), King('white'), Bishop('white'), Knight('white'), Rook('white')]]

    def initialize_buttons(self):
        '''Creates the 2d list of QPushButtons so the internal state can update these for the GUI to see visually
        Could have possibly made a list comprehension, but figured this was easier (not more elegent for sure)'''
        self.buttons = [[QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()],\
                        [QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()],\
                        [QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()],\
                        [QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()],\
                        [QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()],\
                        [QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()],\
                        [QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()],\
                        [QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()]]

    def setup_board(self):
        """ Sets up the board with pieces in their respective starting positions """
        for row in range(8):
            for col in range(8):
                button = self.buttons[row][col]
                self.invis_button(row, col) # Makes the buttons transparent visually

                button.setFixedSize(80, 80) # Sets the Button size
                button.clicked.connect(lambda _, row=row, col=col: self.piece_selected(row, col)) # Connects to the move logic

                # Create a square label (the visual board in the background)
                square = QLabel()
                square.setFixedSize(80, 80)
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                square.setStyleSheet(f"background-color: {color}; border: 1px solid #000;")

                self.grid.addWidget(square, row + 2, col + 2)
                self.grid.addWidget(button, row + 2, col + 2)

        self.refresh_board() # Updates the board with current game state

    def invis_button(self, row, col):
        ''' Stylesheet that can be called on easily to make the button transparent'''
        self.buttons[row][col].setStyleSheet('background-color: transparent;\
                            border: none;\
                            padding: 0px;\
                            margin: 0px;\
                            outline: none;\
                            color: black;\
                            font-size: 50px;')
        
    def refresh_board(self):
        '''Refreshes the GUI board to match the state of the internal game (self.pieces)'''
        for row in range(8):
            for col in range(8):
                self.buttons[row][col].setText(self.pieces[row][col].icon)

                
    def highlight_moves(self, row, col):
        """ Highlight all valid moves for the selected piece """
        piece = self.pieces[row][col]
        for r in range(8):
            for c in range(8):
                if piece.can_move(row, col, r, c, self.pieces):
                    self.buttons[r][c].setStyleSheet('background-color: yellow; font-size: 50px')


    def piece_selected(self, row, col):
        '''Handles all the logic that comes with managing the buttons being clicked'''
        # Reset highlights
        self.reset_highlight()

        # If none of the pieces have been selected
        if self.row is None and self.col is None:
            if not isinstance(self.pieces[row][col], Empty) and self.pieces[row][col].color == self.turn:
                # Start the timer only on the first piece selection
                if not self.timer_running: # Checks if timer is already running 
                    self.timer.start(1000)  # 1-second intervals timer (calls update_timer every 1 second   )
                    self.timer_running = True # Prevents the timer from starting again 

                self.row, self.col = row, col
                self.buttons[row][col].setStyleSheet('background-color: lightgreen; font-size: 50px')
                print(f'Selected: {self.pieces[row][col]} at ({row}, {col})')
                self.highlight_moves(row, col)
            else:
                print('Invalid selection. Please select a valid piece.')

        # Makes sures to validate a move if a piece has already been selected
        else:
            selected_piece = self.pieces[self.row][self.col]
            target_piece = self.pieces[row][col]

            if selected_piece.can_move(self.row, self.col, row, col, self.pieces):
                print(f'Moving {selected_piece} from ({self.row}, {self.col}) to ({row}, {col})')

                # Update score when capturing a piece
                if not isinstance(target_piece, Empty):
                    if self.turn == 'white':
                        self.white_score += target_piece.point
                    else:
                        self.black_score += target_piece.point
                    self.update_score_display(row, col)
                
                # Moves the piece, plus updates the game
                self.pieces[row][col] = selected_piece
                self.pieces[self.row][self.col] = Empty()
                self.refresh_board()
                self.reset_highlight()

                # Reset row and column selection
                self.row, self.col = None, None
                self.other_turn()

                # check for win condition (if king dies)
                white_king_in = False
                black_king_in = False
                for r in range(8):
                    for c in range(8):
                        piece = self.pieces[r][c]
                        if isinstance(piece, King):
                            if piece.color == 'white':
                                white_king_in = True
                            elif piece.color == 'black':
                                black_king_in = True
                if white_king_in == False:
                    self.turn_label.setText('Black wins by DEATH')
                elif black_king_in == False:
                    self.turn_label.setText('White wins by DEATH')

            else:
                print('Invalid move. Please select a valid destination.')
                self.row, self.col = None, None

    def reset_highlight(self):
        """ Reset all button highlights to their default board colors """
        for row in range(8):
            for col in range(8):
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                self.buttons[row][col].setStyleSheet(f'background-color: {color}; font-size: 50px; color: black;')


    def other_turn(self):
        """ Switch turns, update turn label, and manage the timer """
        if self.turn == 'white':
            self.turn = 'black'
        else:
            self.turn = 'white'

        # Update the turn label
        self.turn_label.setText(f"{self.turn.capitalize()}'s Turn")

        # Timer will continue running for the active player
        self.timer_running = True


    def update_timer(self):
        """ Update the timer for the player whose turn it is """
        if self.turn == 'white':
            self.white_time -= 1
            if self.white_time <= 0:
                self.timer.stop()
                self.turn_label.setText("Black Wins by Timeout!")
            self.clock.setText(f'Black Time: {self.black_time}\n\n---------\n\nWhite Time: {self.white_time}')
        elif self.turn == 'black':
            self.black_time -= 1
            if self.black_time <= 0:
                self.timer.stop()
                self.turn_label.setText("White Wins by Timeout!")
            self.clock.setText(f'Black Time: {self.black_time}\n\n---------\n\nWhite Time: {self.white_time}')

                

    def displays(self):
        '''Creates the other elements on the GUI, not the board but clock score etc..'''
        self.grid.addWidget(QLabel(), 0, 2, 1, 8)

        # Black score
        self.black_score_label = QLabel(f'Black Score: {self.black_score}')
        self.black_score_label.setStyleSheet('border: 2px solid white; font-size: 25px; text-align: center; padding: 10px;')
        self.grid.addWidget(self.black_score_label, 1, 2, 1, 4)

        # White score
        self.white_score_label = QLabel(f'White Score: {self.white_score}')
        self.white_score_label.setStyleSheet('border: 2px solid white; font-size: 25px; text-align: center; padding: 10px;')
        self.grid.addWidget(self.white_score_label, 11, 2, 1, 4)

        self.grid.addWidget(QLabel(), 2, 0, 8, 1)
        # Timer display
        self.clock = QLabel(f'Black Time: {self.black_time}\n\n---------\n\nWhite Time: {self.white_time}')
        self.clock.setStyleSheet('border: 2px solid white; font-size: 30px; padding: 10px;')
        self.grid.addWidget(self.clock, 3, 1, 6, 1)

        # Turn display
        self.turn_label = QLabel(f"White's Turn")
        self.turn_label.setStyleSheet('border: 2px solid white; font-size: 30px; font-weight: bold; text-align: center; padding: 10px;')
        self.grid.addWidget(self.turn_label, 1, 6, 1, 4)

        # Restart button
        restart = QPushButton('Restart Game')
        restart.setStyleSheet('background-color: red; color: white; font-size: 25px; padding: 10px;')
        self.grid.addWidget(restart, 11, 6, 1, 4)
        restart.clicked.connect(self.clicked_restart)
        
        self.grid.addWidget(QLabel(), 2, 12)
        self.grid.addWidget(QLabel(), 2, 13)
        self.grid.addWidget(QLabel(), 13, 2)

    def update_score_display(self, row:int=None, col:int=None):
        """ Update the score labels. """
        if row == None and col == None:
            self.black_score_label.setText(f'Black Score: {self.black_score}')
            self.white_score_label.setText(f'White Score: {self.white_score}')
        elif self.turn == 'black':
            self.white_icons += self.pieces[row][col].icon
            self.black_score_label.setText(f'{self.white_icons}: {self.black_score}')
        elif self.turn == 'white':
            self.black_icons += self.pieces[row][col].icon
            self.white_score_label.setText(f'{self.black_icons}: {self.white_score}')


    def clicked_restart(self):
        '''Sets up/resets all the info for a new game'''
        dialog = DialogConfirmation()
        if dialog.exec():
            # Resets the game 
            self.turn = 'white'
            self.initialize_pieces() # Reset the pieces 
            self.refresh_board() # Refreshes the GUI 

            # Reset scores
            self.white_score = 0
            self.black_score = 0
            self.update_score_display()

            # Resets the timer with 30 seconds
            self.white_time = self.timer_time
            self.black_time = self.timer_time  
            self.timer.stop()  # Stop's timer
            self.timer_running = False  # Reset's timer 

            # Update the clock display
            self.clock.setText(f'Black Time: {self.black_time}\n\n---------\n\nWhite Time: {self.white_time}')

            # Reset the turn label
            self.turn_label.setText(f"White's Turn")



class DialogConfirmation(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Wait a second...')

        dialog_button = QDialogButtonBox.Yes | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(dialog_button)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel('You are sure?')
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication()
    window = Chess()
    window.show()
    app.exec()
    