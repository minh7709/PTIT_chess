"""
Handling the AI moves.
Có sử dụng thuật toán Negamax và cắt tỉa Alpha-beta
"""
import random

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
#Đánh giá mức độ quan trọng của từng quân cờ (VD: 0 là không thể để mất,Q là quan trọng nhất và chỉ mang tính tương đối)

knight_scores_opening = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.3, 0.3, 0.3, 0.3, 0.55, 0.2],
                 [0.2, 0.5, 0.3, 0.3, 0.3, 0.3, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores_opening = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores_opening = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores_opening = [[0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]]

pawn_scores_opening = [[6, 6, 6, 6, 6, 6, 6, 6],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.45, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

knight_scores_ending = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores_ending = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores_ending = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores_ending = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores_ending = [[ 7,  7,  7,  7,  7,  7,  7,  7],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": [knight_scores_opening, knight_scores_ending],
                         "bN": [knight_scores_opening[::-1], bishop_scores_ending[::-1]],
                         "wB": [bishop_scores_opening, bishop_scores_ending], 
                         "bB": [bishop_scores_opening[::-1], bishop_scores_ending[::-1]],
                         "wQ": [queen_scores_opening, queen_scores_ending], 
                         "bQ": [queen_scores_opening[::-1], queen_scores_ending[::-1]],
                         "wR": [rook_scores_opening, rook_scores_ending], 
                         "bR": [rook_scores_opening[::-1], rook_scores_ending[::-1]],
                         "wp": [pawn_scores_opening, pawn_scores_ending ], 
                         "bp": [pawn_scores_opening[::-1], pawn_scores_ending[::-1]]}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

opening_book = {
    (): ["e2e4", "d2d4", "c2c4", "g1f3"],                    # Nước đầu tiên của Trắng
    ("e2e4",): ["e7e5", "c7c5"],                             # Phản hồi của Đen cho 1.e4
    ("d2d4",): ["d7d5", "g8f6"],                             # Phản hồi của Đen cho 1.d4
    ("c2c4",): ["e7e5", "g8f6"],                             # Phản hồi của Đen cho 1.c4
    ("g1f3",): ["d7d5", "g8f6"],                             # Phản hồi của Đen cho 1.Nf3
    # Có thể bổ sung thêm các nhánh khai cuộc khác...
}


def findBestMove(game_state, valid_moves, return_queue):
    global next_move
    next_move = None

 # Kiểm tra opening book trước khi tìm kiếm
    book_move = getBookMove(game_state, valid_moves)
    if book_move is not None:
        # Nếu có nước đi trong khai cuộc, chọn nước đó
        return_queue.put(book_move)
        return

    random.shuffle(valid_moves)
    findMoveNegaMaxAlphaBeta(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                             1 if game_state.white_to_move else -1)
    return_queue.put(next_move)

def getBookMove(game_state, valid_moves):
    """
    Kiểm tra và lấy nước đi từ opening book (nếu có) dựa trên lịch sử nước đi của game_state.
    Trả về move nếu tìm thấy, hoặc None nếu không có nước nào trong book.
    """
    # Lấy lịch sử nước đi dưới dạng tuple các string (vd: ("e2e4", "e7e5", ...))
    if hasattr(game_state, "move_log"):
        history = tuple(move_to_notation(m) for m in game_state.move_log)
    else:
        history = ()
    # Kiểm tra các khóa trong opening_book khớp với lịch sử hiện tại
    if history in opening_book:
        # Lấy danh sách nước đi khả dĩ từ book và chọn ngẫu nhiên một nước
        move_notation = random.choice(opening_book[history])
        # Chuyển notation thành đối tượng Move tương ứng trong valid_moves
        for move in valid_moves:
            if move_to_notation(move) == move_notation:
                return move
    return None

def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * scoreBoard(game_state)
    # move ordering - implement later //TODO
        # Sắp xếp nước đi (Move ordering) - ưu tiên các nước bắt quân theo MVV-LVA
    valid_moves.sort(key=lambda move: (10 * piece_score[move.piece_captured[1]] - piece_score[move.piece_moved[1]]) 
                     if move.piece_captured != "--" else -1, reverse=True)
    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        game_state.undoMove()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score

def quiescence_search(game_state, alpha, beta, turn_multiplier):
    """
    Thực hiện Quiescence Search: tìm kiếm tĩnh tại vị trí hiện tại bằng cách 
    mở rộng các nước bắt quân cho đến khi vị trí yên tĩnh.
    """
    # Đánh giá tĩnh của vị trí hiện tại
    stand_pat = turn_multiplier * scoreBoard(game_state)
    if stand_pat >= beta:
        # Nếu đánh giá vượt ngưỡng beta, cắt tỉa (beta cutoff)
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    # Lấy tất cả các nước đi hợp lệ rồi lọc chỉ giữ nước bắt quân (captures)
    moves = game_state.getValidMoves()
    capture_moves = [m for m in moves if m.pieceCaptured != "--"]
    # Sắp xếp các nước bắt quân theo MVV-LVA để cắt tỉa hiệu quả hơn
    capture_moves.sort(key=lambda move: (10 * piece_score[move.pieceCaptured[1]] - piece_score[move.pieceMoved[1]]), 
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

def move_to_notation(move):
    """
    Chuyển một đối tượng move thành chuỗi ký hiệu tọa độ (ví dụ: e2e4).
    Giả định: hàng 0 = rank 8, cột 0 = file 'a'.
    """
    start_rank = 8 - move.start_row   # rank = 8 - chỉ số hàng
    end_rank = 8 - move.end_row
    start_file = chr(ord('a') + move.start_col)
    end_file = chr(ord('a') + move.end_col)
    return f"{start_file}{start_rank}{end_file}{end_rank}"

def scoreBoard(game_state):
    """
    Score the board. A positive score is good for white, a negative score is good for black.
    """
    if game_state.checkmate:
        if game_state.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif game_state.stalemate:
        return STALEMATE #Hòa
    #Chưa hiểu tạo score làm gì
    score = 0 #Nếu không có tình huống checkmate hay stalemate thì khởi tạo score
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_position_score = 0
                if piece[1] != "K":
                    if len(game_state.move_log)//2 <= 10:
                        piece_position_score = piece_position_scores[piece][0][row][col]
                    else:
                        piece_position_score = piece_position_scores[piece][1][row][col]
                if piece[0] == "w":
                    score += piece_score[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= piece_score[piece[1]] + piece_position_score
    # King safety (an toàn của vua): đếm số quân cùng màu xung quanh vua (8 ô xung quanh)
    KING_SAFETY_BONUS = 0.05
    white_king_pos = game_state.white_king_location
    black_king_pos = game_state.black_king_location
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
    white_score = KING_SAFETY_BONUS * defenders
    # Đếm quân bảo vệ quanh vua đen
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
    black_score = KING_SAFETY_BONUS * defenders

    return score + white_score - black_score


def findRandomMove(valid_moves):
    """
    Picks and returns a random valid move.
    """
    return random.choice(valid_moves)
