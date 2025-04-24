"""
Chess AI with Negamax, Alpha-Beta pruning, Quiescence Search, MVV-LVA move ordering,
enhanced evaluation (king safety, pawn structure, mobility), and an opening book.
"""
import random

# Basic piece values
piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

# Piece-square tables for each piece type – used to evaluate the relative position of pieces on the board
knight_scores = [
    [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
    [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
    [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
    [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
    [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
    [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
    [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
    [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]
]
bishop_scores = [
    [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
    [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
    [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
    [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
    [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
    [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
    [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]
]
rook_scores = [
    [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]
]
queen_scores = [
    [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
    [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
    [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
    [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
    [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
    [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]
]
pawn_scores = [
    [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
    [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
    [0.25, 0.25, 0.3, 0.7, 0.7, 0.3, 0.25, 0.25],
    [0.2, 0.2, 0.2, 0.7, 0.7, 0.2, 0.2, 0.2],
    [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
    [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
    [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
]

# Positional scores by piece type (adjusted for color)
piece_position_scores = {
    "wN": knight_scores,
    "bN": knight_scores[::-1],  # reversed for black (because the above table is for white from rank 1->8)
    "wB": bishop_scores,
    "bB": bishop_scores[::-1],
    "wQ": queen_scores,
    "bQ": queen_scores[::-1],
    "wR": rook_scores,
    "bR": rook_scores[::-1],
    "wp": pawn_scores,
    "bp": pawn_scores[::-1]
}

# Scores for special endgame conditions
CHECKMATE = 10000  # very high value for checkmate
STALEMATE = 0      # draw

# Maximum search depth for Negamax algorithm (not including quiescence)
DEPTH = 3

# Simple opening book: sample openings (in coordinate notation)
opening_book = {
    (): ["e2e4", "d2d4", "c2c4", "g1f3"],                    # White's first move
    ("e2e4",): ["e7e5", "c7c5"],                             # Black's response to 1.e4
    ("d2d4",): ["d7d5", "g8f6"],                             # Black's response to 1.d4
    ("c2c4",): ["e7e5", "g8f6"],                             # Black's response to 1.c4
    ("g1f3",): ["d7d5", "g8f6"],                             # Black's response to 1.Nf3
    # More opening lines can be added...
}

def find_best_move(game_state, valid_moves, return_queue):
    global next_move, DEPTH
    next_move = None

    # Nếu không có nước đi hợp lệ, trả về None
    if not valid_moves:
        return_queue.put(None)
        return

    # Kiểm tra sách khai cuộc (nếu có)
    book_move = get_book_move(game_state, valid_moves)
    if book_move is not None:
        return_queue.put(book_move)
        return

    # Không dùng sách, thực hiện tìm kiếm theo iterative deepening
    random.shuffle(valid_moves)
    best_score = -CHECKMATE
    best_move = None
    turn_multiplier = 1 if game_state.white_to_move else -1
    original_depth = DEPTH

    # Lặp tìm kiếm từ độ sâu 1 đến DEPTH
    for depth in range(1, original_depth + 1):
        DEPTH = depth
        score = find_move_nega_max_alpha_beta(
            game_state, valid_moves, depth,
            -CHECKMATE, CHECKMATE,
            turn_multiplier
        )
        if score > best_score:
            best_score = score
            best_move = next_move
        else:
            next_move = best_move

    DEPTH = original_depth
    return_queue.put(next_move)

    return_queue.put(next_move)


def get_book_move(game_state, valid_moves):
    """
    Check and retrieve a move from the opening book (if available) based on the game_state's move history.
    Return the move if found, or None if no move is found in the book.
    """
    # Get the move history as a tuple of strings (e.g., ("e2e4", "e7e5", ...))
    if hasattr(game_state, "move_log"):
        history = tuple(move_to_notation(m) for m in game_state.move_log)
    else:
        history = ()
    # Check if any keys in opening_book match the current history
    if history in opening_book:
        # Take the list of possible moves from the book and choose one at random
        move_notation = random.choice(opening_book[history])
        # Convert the notation to the corresponding Move object in valid_moves
        for move in valid_moves:
            if move_to_notation(move) == move_notation:
                return move
    return None


def move_to_notation(move):
    """
    Convert a move object to coordinate notation string (e.g., e2e4).
    Assumes: row 0 = rank 8, col 0 = file 'a'.
    """
    start_rank = 8 - move.start_row   # rank = 8 - row index
    end_rank = 8 - move.end_row
    start_file = chr(ord('a') + move.start_col)
    end_file = chr(ord('a') + move.end_col)
    return f"{start_file}{start_rank}{end_file}{end_rank}"


def find_move_nega_max_alpha_beta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    """
    Negamax search algorithm with Alpha-Beta pruning.
    Returns the best score found for the current state.
    """
    global next_move
    # Check stopping condition
    if depth == 0:
        # Use quiescence search at leaf node
        return quiescence_search(game_state, alpha, beta, turn_multiplier)

    # Order moves (move ordering) - prioritize capturing moves by MVV-LVA
    valid_moves.sort(key=lambda move: (10 * piece_score[move.piece_captured[1]] - piece_score[move.piece_moved[1]])
                     if move.piece_captured != "--" else -1,
                     reverse=True)

    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()
        # Recursively call Negamax for opponent (score sign inverted and alpha-beta bounds swapped)
        score = -find_move_nega_max_alpha_beta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        game_state.undoMove()

        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move  # store the best move at root depth
        # Update alpha threshold
        if max_score > alpha:
            alpha = max_score
        # Alpha-beta cutoff
        if alpha >= beta:
            break
    return max_score


def quiescence_search(game_state, alpha, beta, turn_multiplier):
    """
    Perform Quiescence Search: extend search at the current position by exploring capture moves 
    until reaching a quiet position.
    """
    # Static evaluation of the current position
    stand_pat = turn_multiplier * score_board(game_state)
    if stand_pat >= beta:
        # If evaluation exceeds beta threshold, cutoff (beta cutoff)
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    # Get all valid moves, then filter to keep only captures
    moves = game_state.getValidMoves()
    capture_moves = [m for m in moves if m.piece_captured != "--"]
    # Sort capture moves by MVV-LVA for more effective pruning
    capture_moves.sort(key=lambda move: (10 * piece_score[move.piece_captured[1]] - piece_score[move.piece_moved[1]]), 
                       reverse=True)

    for move in capture_moves:
        game_state.makeMove(move)
        score = -quiescence_search(game_state, -beta, -alpha, -turn_multiplier)
        game_state.undoMove()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha


def score_board(game_state):
    """
    Evaluate the current board and return a score.
    Positive score is good for White, negative score is good for Black.
    """
    # If the game is over
    if game_state.checkmate:
        # If it's White's turn and checkmated -> White loses (maximum negative score)
        if game_state.white_to_move:
            return -CHECKMATE
        else:
            # If it's Black's turn and checkmated -> Black loses
            return CHECKMATE
    if game_state.stalemate:
        return STALEMATE

    # Calculate score for each side
    white_score = 0
    black_score = 0

    # Traverse the entire board
    for r in range(len(game_state.board)):
        for c in range(len(game_state.board[r])):
            piece = game_state.board[r][c]
            if piece == "--":
                continue  # empty square
            # Basic piece value + positional value for the piece, depending on color
            piece_type = piece[1]  # piece symbol (K, Q, R, B, N, p)
            if piece_type != "K":  # can add positional score for all pieces except the king
                piece_position_score = piece_position_scores[piece][r][c]
            else:
                piece_position_score = 0  # do not use position table for king
            if piece[0] == "w":
                white_score += piece_score[piece_type] + piece_position_score
            else:
                black_score += piece_score[piece_type] + piece_position_score

    # Pawn structure: evaluate doubled, isolated, and passed pawns
    # Collect positions of each side's pawns by file
    white_pawns = []
    black_pawns = []
    pawn_files_white = {}
    pawn_files_black = {}
    for r in range(len(game_state.board)):
        for c in range(len(game_state.board[r])):
            piece = game_state.board[r][c]
            if piece == "--":
                continue
            if piece == "wp":
                white_pawns.append((r, c))
                pawn_files_white[c] = pawn_files_white.get(c, 0) + 1
            elif piece == "bp":
                black_pawns.append((r, c))
                pawn_files_black[c] = pawn_files_black.get(c, 0) + 1

    # Doubled pawns: penalty for each extra pawn on the same file
    DOUBLED_PAWN_PENALTY = 0.5
    for count in pawn_files_white.values():
        if count > 1:
            # if there are n pawns on the same file, penalize (n-1) of them (for white_score)
            white_score -= DOUBLED_PAWN_PENALTY * (count - 1)
    for count in pawn_files_black.values():
        if count > 1:
            black_score -= DOUBLED_PAWN_PENALTY * (count - 1)

    # Isolated pawns: no same-color pawn on adjacent files
    ISOLATED_PAWN_PENALTY = 0.5
    for (r, c) in white_pawns:
        # if no white pawn on file c-1 or c+1
        if (c - 1 not in pawn_files_white) and (c + 1 not in pawn_files_white):
            white_score -= ISOLATED_PAWN_PENALTY
    for (r, c) in black_pawns:
        if (c - 1 not in pawn_files_black) and (c + 1 not in pawn_files_black):
            black_score -= ISOLATED_PAWN_PENALTY

    # Passed pawns: pawn with no opposing pawn blocking its path forward
    PASSED_PAWN_BONUS = 0.5
    # Check each white pawn: no black pawn ahead on the same or adjacent file
    for (wr, wc) in white_pawns:
        passed = True
        for (br, bc) in black_pawns:
            if bc in {wc - 1, wc, wc + 1} and br < wr:
                # There is a black pawn in front (a smaller row index means it's above on the board)
                passed = False
                break
        if passed:
            white_score += PASSED_PAWN_BONUS
    # Do the same for each black pawn
    for (br, bc) in black_pawns:
        passed = True
        for (wr, wc) in white_pawns:
            if wc in {bc - 1, bc, bc + 1} and wr > br:
                # There is a white pawn ahead of the black pawn's path
                passed = False
                break
        if passed:
            black_score += PASSED_PAWN_BONUS

    # King safety: count the number of same-color pieces around the king (the 8 surrounding squares)
    KING_SAFETY_BONUS = 0.1
    white_king_pos = None
    black_king_pos = None
    # Find the position of the white king and black king
    for r in range(len(game_state.board)):
        for c in range(len(game_state.board[r])):
            if game_state.board[r][c] == "wK":
                white_king_pos = (r, c)
            elif game_state.board[r][c] == "bK":
                black_king_pos = (r, c)
    # Count pieces defending the white king
    if white_king_pos is not None:
        wr, wc = white_king_pos
        defenders = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = wr + dr, wc + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    piece = game_state.board[nr][nc]
                    if piece != "--" and piece[0] == "w":
                        defenders += 1
        white_score += KING_SAFETY_BONUS * defenders
    # Count pieces defending the black king
    if black_king_pos is not None:
        br, bc = black_king_pos
        defenders = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = br + dr, bc + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    piece = game_state.board[nr][nc]
                    if piece != "--" and piece[0] == "b":
                        defenders += 1
        black_score += KING_SAFETY_BONUS * defenders

    # Mobility: count the number of valid moves for White and Black
    # Save current turn state to restore later
    current_turn = game_state.white_to_move
    # Number of White's moves
    game_state.white_to_move = True
    white_moves = game_state.getValidMoves()
    # Number of Black's moves
    game_state.white_to_move = False
    black_moves = game_state.getValidMoves()
    # Restore the turn state
    game_state.white_to_move = current_turn

    MOBILITY_WEIGHT = 0.1
    white_score += MOBILITY_WEIGHT * len(white_moves)
    black_score += MOBILITY_WEIGHT * len(black_moves)

    # Total score = White's score - Black's score (positive: advantage White, negative: advantage Black)
    return white_score - black_score


def find_random_move(valid_moves):
    """Pick a random valid move."""
    return random.choice(valid_moves)
