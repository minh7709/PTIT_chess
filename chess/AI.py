"""
Handling the AI moves.
Có sử dụng thuật toán Negamax và cắt tỉa Alpha-beta
"""
import random
from Score import piece_score, piece_position_scores
from Book_move import opening_book

CHECKMATE = 1000
STALEMATE = 0
    
def findBestMove(game_state, valid_moves, return_queue, max_depth = 3):
    global next_move
    next_move = None
    if len(valid_moves) <= 27 and len(game_state.move_log) > 12: max_depth = 4
 # Kiểm tra opening book trước khi tìm kiếm
    book_move = getBookMove(game_state, valid_moves)
    if book_move is not None:
        # Nếu có nước đi trong khai cuộc, chọn nước đó
        return_queue.put(book_move)
        return

    findMoveNegaMaxAlphaBeta(game_state, valid_moves, max_depth, max_depth, -CHECKMATE, CHECKMATE,
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

def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, max_depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return quiescence_search(game_state, alpha, beta, turn_multiplier)
    # move ordering - implement later //
    # Sắp xếp nước đi (Move ordering) - ưu tiên các nước bắt quân theo MVV-LVA
    valid_moves = order_moves(game_state, valid_moves)
    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(game_state, next_moves, depth - 1, max_depth, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == max_depth:
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
    capture_moves = [m for m in moves if m.piece_captured != "--"]
    # Sắp xếp các nước bắt quân theo MVV-LVA để cắt tỉa hiệu quả hơn
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

def order_moves(gs, moves):
    def key(m):
        score = 0
        # 1. Bắt quân → MVV-LVA
        if m.piece_captured != "--":
            vic = piece_score[m.piece_captured[1]]
            atk = piece_score[m.piece_moved[1]]
            score += 500 + (vic*10 - atk)
        # 2. Phong cấp
        if m.is_pawn_promotion:
            score += 800
        # 3. Nhập thành
        if m.is_castle_move:
            score += 500
        # 4. Nước chiếu
        gs.makeMove(m)
        if gs.inCheck():
            score += 200
        gs.undoMove()
        return score
    return sorted(moves, key=key, reverse=True)


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

    white_score = 0 
    black_score = 0
    white_cnt = 0
    black_cnt = 0
    white_pawns = []
    black_pawns = []
    pawn_files_white = {k : 0 for k in range(8)}
    pawn_files_black = {k : 0 for k in range(8)}

    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                if piece[0] == "w":
                    white_cnt += 1
                if piece[0] == "b":
                    black_cnt += 1
                if piece[1] == "p" and piece[0] == "w":
                    white_pawns.append((row, col))
                    pawn_files_white[col] += 1
                if piece[1] == "p" and piece[0] == "b":
                    black_pawns.append((row, col))
                    pawn_files_black[col] += 1

    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_position_score = 0
                if white_cnt + black_cnt > 16:
                    piece_position_score = piece_position_scores[piece][0][row][col]
                else:
                    piece_position_score = piece_position_scores[piece][1][row][col]
                if piece[0] == 'w':
                    white_score += piece_score[piece[1]] + piece_position_score
                else: black_score += piece_score[piece[1]] + piece_position_score

    # King safety (an toàn của vua): đếm số quân cùng màu xung quanh vua (8 ô xung quanh)
    white_king_pos = game_state.white_king_location
    black_king_pos = game_state.black_king_location

    #dem quan tot trang va den truoc mat vua
    NO_FRONT_PAWN = 0.5
    if pawn_files_white[white_king_pos[1]] == 0:
        white_score -= NO_FRONT_PAWN
    if pawn_files_black[black_king_pos[1]] == 0:
        black_score -= NO_FRONT_PAWN  
    
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
    white_score += KING_SAFETY_BONUS * defenders
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
    black_score += KING_SAFETY_BONUS * defenders


    #pawns structure: cấu trúc tốt:
    # 1. Doubled
    DOUBLED_PAWN_PENALTY = 0.2
    for idx in range(8):
        if pawn_files_white[idx] > 1:
            white_score -= DOUBLED_PAWN_PENALTY * (pawn_files_white[idx] - 1)
        if pawn_files_black[idx] > 1:
            black_score -= DOUBLED_PAWN_PENALTY * (pawn_files_black[idx] - 1)

    # 2. Isolated
    ISOLATED_PAWN_PENALTY = 0.2
    for (_, c) in white_pawns:
        left_empty  = (c == 0) or (pawn_files_white[c-1] == 0)
        right_empty = (c == 7) or (pawn_files_white[c+1] == 0)
        if left_empty and right_empty:
            white_score -= ISOLATED_PAWN_PENALTY
    for (_, c) in black_pawns:
        left_empty  = (c == 0) or (pawn_files_black[c-1] == 0)
        right_empty = (c == 7) or (pawn_files_black[c+1] == 0)
        if left_empty and right_empty:
            black_score -= ISOLATED_PAWN_PENALTY

    # 3. Passed
    PASSED_BONUS = 0.2
    for (wr, wc) in white_pawns:
        if all(not (bc in (wc-1, wc, wc+1) and br < wr) for br, bc in black_pawns):
            white_score += PASSED_BONUS
    for (br, bc) in black_pawns:
        if all(not (wc in (bc-1, bc, bc+1) and wr > br) for wr, wc in white_pawns):
            black_score += PASSED_BONUS

    return white_score - black_score
    
def findRandomMove(valid_moves):
    """
    Picks and returns a random valid move.
    """
    return random.choice(valid_moves)
