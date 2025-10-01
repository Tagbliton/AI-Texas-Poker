import random
from typing import List, Dict, Tuple, Optional
from enum import Enum
from collections import Counter
from itertools import combinations



class Suit(Enum):
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'
    SPADES = '♠'


class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        rank_value = self.rank.value
        if rank_value == 11:
            rank_str = "J"
        elif rank_value == 12:
            rank_str = "Q"
        elif rank_value == 13:
            rank_str = "K"
        elif rank_value == 14:
            rank_str = "A"
        elif rank_value == 10:
            rank_str = "T"
        else:
            rank_str = str(rank_value)
        return f"{rank_str}{self.suit.value}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other):
        return self.rank.value < other.rank.value

    def __hash__(self):
        return hash((self.rank, self.suit))


class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if not self.cards:
            raise ValueError("牌堆已空，无法发牌")
        return self.cards.pop()


class HandRank(Enum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9


class PokerHandEvaluator:
    @staticmethod
    def evaluate_hand(player_cards: List[Card], community_cards: List[Card]) -> Tuple[HandRank, List[int]]:
        all_cards = player_cards + community_cards

        best_hand_rank = HandRank.HIGH_CARD
        best_tie_breaker = []

        for hand_combo in combinations(all_cards, 5):
            current_rank, current_tie_breaker = PokerHandEvaluator._evaluate_5_card_hand(list(hand_combo))
            if current_rank.value > best_hand_rank.value:
                best_hand_rank = current_rank
                best_tie_breaker = current_tie_breaker
            elif current_rank.value == best_hand_rank.value:
                for i in range(len(current_tie_breaker)):
                    if current_tie_breaker[i] > best_tie_breaker[i]:
                        best_tie_breaker = current_tie_breaker
                        break
                    if current_tie_breaker[i] < best_tie_breaker[i]:
                        break

        return best_hand_rank, best_tie_breaker

    @staticmethod
    def _evaluate_5_card_hand(hand: List[Card]) -> Tuple[HandRank, List[int]]:
        hand.sort(key=lambda c: c.rank.value, reverse=True)
        ranks = [card.rank.value for card in hand]
        suits = [card.suit for card in hand]

        is_flush = len(set(suits)) == 1

        unique_ranks = sorted(list(set(ranks)), reverse=True)
        is_straight = len(unique_ranks) == 5 and (unique_ranks[0] - unique_ranks[4] == 4)

        is_wheel_straight = unique_ranks == [14, 5, 4, 3, 2]
        if is_wheel_straight:
            is_straight = True
            ranks = [5, 4, 3, 2, 1]

        if is_straight and is_flush:
            if unique_ranks == [14, 13, 12, 11, 10]:
                return HandRank.ROYAL_FLUSH, [14]
            return HandRank.STRAIGHT_FLUSH, [ranks[0]]

        rank_counts = Counter(ranks)
        sorted_rank_counts = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

        counts = [c[1] for c in sorted_rank_counts]
        main_ranks = [c[0] for c in sorted_rank_counts]

        if counts[0] == 4:
            return HandRank.FOUR_OF_A_KIND, [main_ranks[0], main_ranks[1]]
        if counts[0] == 3 and counts[1] == 2:
            return HandRank.FULL_HOUSE, [main_ranks[0], main_ranks[1]]
        if is_flush:
            return HandRank.FLUSH, ranks
        if is_straight:
            return HandRank.STRAIGHT, [ranks[0]]
        if counts[0] == 3:
            kickers = [r for r in main_ranks if r != main_ranks[0]]
            return HandRank.THREE_OF_A_KIND, [main_ranks[0]] + kickers[:2]
        if counts[0] == 2 and counts[1] == 2:
            pairs = sorted([main_ranks[0], main_ranks[1]], reverse=True)
            kicker = main_ranks[2]
            return HandRank.TWO_PAIR, pairs + [kicker]
        if counts[0] == 2:
            kickers = [r for r in main_ranks if r != main_ranks[0]]
            return HandRank.PAIR, [main_ranks[0]] + kickers[:3]
        return HandRank.HIGH_CARD, ranks


class Player:
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.bet_in_round = 0
        self.bet_in_hand = 0
        self.has_folded = False
        self.is_all_in = False

    def reset_for_hand(self):
        self.hand = []
        self.bet_in_round = 0
        self.bet_in_hand = 0
        self.has_folded = False
        self.is_all_in = False

    def bet(self, amount: int) -> int:
        actual_bet = min(amount, self.chips)
        self.chips -= actual_bet
        self.bet_in_round += actual_bet
        self.bet_in_hand += actual_bet
        if self.chips == 0:
            self.is_all_in = True
        return actual_bet

    def __repr__(self):
        status = " (已弃牌)" if self.has_folded else " (已全下)" if self.is_all_in else ""
        return f"{self.name}: 手牌{self.hand}, 筹码{self.chips}, 本轮下注{self.bet_in_round}{status}"


class PokerGame:
    def __init__(self, player_names: List[str], initial_chips: int = 1000, log_file: str = "poker_game_log.txt"):
        self.players = [Player(name, initial_chips) for name in player_names]
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_betting_round = ""
        self.small_blind_amount = 10
        self.big_blind_amount = 20
        self.dealer_index = -1
        self.log_file = log_file

    def log_message(self, message: str):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def reset_hand(self):
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        if self.players:
            self.dealer_index = (self.dealer_index + 1) % len(self.players)
        for player in self.players:
            player.reset_for_hand()

    def deal_hole_cards(self):
        start_index = (self.dealer_index + 1) % len(self.players)
        for i in range(len(self.players) * 2):
            player_index = (start_index + i) % len(self.players)
            self.players[player_index].hand.append(self.deck.deal_card())

    def _deal_community(self, count: int):
        if self.deck.cards: self.deck.deal_card()
        for _ in range(count):
            if self.deck.cards: self.community_cards.append(self.deck.deal_card())

    def deal_flop(self):
        self._deal_community(3)

    def deal_turn(self):
        self._deal_community(1)

    def deal_river(self):
        self._deal_community(1)

    def post_blinds(self):
        num_players = len(self.players)
        if num_players < 2: return

        sb_index = (self.dealer_index + 1) % num_players
        bb_index = (self.dealer_index + 2) % num_players

        if num_players == 2:
            sb_index = self.dealer_index
            bb_index = (self.dealer_index + 1) % num_players

        sb_player = self.players[sb_index]
        sb_bet = sb_player.bet(self.small_blind_amount)
        self.pot += sb_bet
        msg = f"{sb_player.name} 下小盲注 {sb_bet}"
        print(msg);
        self.log_message(msg)

        bb_player = self.players[bb_index]
        bb_bet = bb_player.bet(self.big_blind_amount)
        self.pot += bb_bet
        msg = f"{bb_player.name} 下大盲注 {bb_bet}"
        print(msg);
        self.log_message(msg)

        msg = f"当前底池: {self.pot}\n"
        print(msg);
        self.log_message(msg)

    def get_active_players(self) -> List[Player]:
        return [p for p in self.players if not p.has_folded]

    def get_betting_round_status(self) -> str:
        status = f"\n--- {self.current_betting_round} ---\n"
        status += f"公共牌: {self.community_cards}\n"
        status += f"当前底池: {self.pot}\n"
        for player in self.players:
            status += f"{player}\n"
        return status

    def betting_round(self):
        num_players = len(self.players)

        if self.current_betting_round == "Pre-flop":
            action_index = (self.dealer_index + 3) % num_players
            if num_players == 2: action_index = self.dealer_index
        else:
            action_index = (self.dealer_index + 1) % num_players

        current_bet = self.big_blind_amount if self.current_betting_round == "Pre-flop" else 0
        min_raise = self.big_blind_amount
        action_closer = None

        if self.current_betting_round == "Pre-flop":
            bb_index = (self.dealer_index + 2) % num_players
            if num_players == 2: bb_index = (self.dealer_index + 1) % num_players
            action_closer = self.players[bb_index]

        players_have_acted = set()

        while True:
            active_players = self.get_active_players()
            if len(active_players) <= 1: break

            player = self.players[action_index % num_players]

            is_round_over = False
            if player == action_closer:
                is_round_over = True
            if action_closer is None and len(players_have_acted) == len(active_players):
                is_round_over = True
            if self.current_betting_round == "Pre-flop" and player == action_closer and current_bet == self.big_blind_amount:
                is_round_over = False

            if is_round_over: break

            if player.has_folded or player.is_all_in:
                action_index += 1
                continue

            players_have_acted.add(player)

            status_msg = f"\n轮到 {player.name} 操作 (筹码: {player.chips})"
            print(status_msg);
            self.log_message(status_msg)

            amount_to_call = current_bet - player.bet_in_round

            valid_actions = ["fold"]
            if amount_to_call == 0:
                valid_actions.append("check")
            elif player.chips > amount_to_call:
                valid_actions.append("call")
            elif player.chips <= amount_to_call:
                valid_actions.append("call")

            if player.chips > amount_to_call:
                valid_actions.append("raise")

            action_input = ""
            prompt_msg = f"你需要跟注 {amount_to_call}。可用操作: {valid_actions}: "
            while action_input not in valid_actions:
                action_input = input(prompt_msg).strip().lower()

            if action_input == "fold":
                player.has_folded = True
                msg = f"{player.name} 弃牌"
                print(msg);
                self.log_message(msg)

            elif action_input == "check":
                msg = f"{player.name} 过牌"
                print(msg);
                self.log_message(msg)

            elif action_input == "call":
                bet_amount = player.bet(amount_to_call)
                self.pot += bet_amount
                msg = f"{player.name} 跟注 {bet_amount}"
                print(msg);
                self.log_message(msg)
                if player.is_all_in: print(f"{player.name} 已全下！")

            elif action_input == "raise":
                min_raise_to = current_bet + min_raise
                max_raise_to = player.chips + player.bet_in_round

                raise_to = 0
                while True:
                    try:
                        raise_to_str = input(f"请输入总下注额 (最小: {min_raise_to}, 最大: {max_raise_to}): ")
                        raise_to = int(raise_to_str)
                        if min_raise_to <= raise_to <= max_raise_to:
                            break
                        else:
                            print("无效金额")
                    except ValueError:
                        print("无效输入")

                amount_to_add = raise_to - player.bet_in_round
                bet_amount = player.bet(amount_to_add)
                self.pot += bet_amount

                min_raise = raise_to - current_bet
                current_bet = raise_to
                action_closer = player
                players_have_acted = {player}

                msg = f"{player.name} 加注到 {current_bet}"
                print(msg);
                self.log_message(msg)
                if player.is_all_in: print(f"{player.name} 已全下！")

            action_index += 1

    def determine_winner(self, players: List[Player]) -> List[Player]:
        if not players: return []
        if len(players) == 1: return players

        results = []
        for player in players:
            rank, tie_breaker = PokerHandEvaluator.evaluate_hand(player.hand, self.community_cards)
            results.append({'player': player, 'rank': rank, 'tie_breaker': tie_breaker})

        results.sort(key=lambda x: (x['rank'].value, x['tie_breaker']), reverse=True)

        best_rank = results[0]['rank']
        best_tie_breaker = results[0]['tie_breaker']

        winners = [res['player'] for res in results if
                   res['rank'] == best_rank and res['tie_breaker'] == best_tie_breaker]
        return winners

    def distribute_pot(self):
        in_hand_players = self.get_active_players()

        if len(in_hand_players) == 1:
            winner = in_hand_players[0]
            msg = f"\n其他玩家都已弃牌, {winner.name} 赢得底池 {self.pot}！"
            print(msg);
            self.log_message(msg)
            winner.chips += self.pot
            return

        # *** BUG FIX: Rewritten side pot calculation logic ***
        pots = []
        committed_players = [p for p in in_hand_players if p.bet_in_hand > 0]
        if not committed_players: return

        pot_levels = sorted(list(set(p.bet_in_hand for p in committed_players)))
        last_level = 0

        for level in pot_levels:
            level_contribution = level - last_level
            players_at_this_level = [p for p in self.players if p.bet_in_hand >= level]
            pot_size = level_contribution * len(players_at_this_level)

            eligible_players = [p for p in players_at_this_level if not p.has_folded]

            if pot_size > 0 and eligible_players:
                pots.append({'size': pot_size, 'eligible_players': eligible_players})

            last_level = level

        for i, pot in enumerate(pots):
            pot_name = f"主池" if i == 0 else f"边池 {i}"
            winners = self.determine_winner(pot['eligible_players'])
            if not winners: continue

            win_amount = pot['size'] // len(winners)
            remainder = pot['size'] % len(winners)

            msg = f"\n--- 结算 {pot_name} (大小: {pot['size']}) ---"
            print(msg);
            self.log_message(msg)

            for winner in winners:
                rank, _ = PokerHandEvaluator.evaluate_hand(winner.hand, self.community_cards)
                hand_name = rank.name.replace('_', ' ').title()
                win_msg = f"{winner.name} 以 {hand_name} ({' '.join(map(str, winner.hand))}) 赢得 {win_amount} 筹码"
                print(win_msg);
                self.log_message(win_msg)
                winner.chips += win_amount

            if remainder > 0:
                for j in range(remainder): winners[j].chips += 1

    def should_skip_to_showdown(self) -> bool:
        """ BUG FIX: New method to check if betting is over due to all-ins. """
        active_players = self.get_active_players()
        # If 0 or 1 active players are not all-in, no more betting can occur.
        players_who_can_bet = [p for p in active_players if not p.is_all_in]
        return len(players_who_can_bet) < 2

    def run_to_showdown(self):
        """ BUG FIX: New method to deal remaining cards and end the round. """
        msg = "\n所有剩余玩家均已全下，直接发完公共牌进行结算..."
        print(msg);
        self.log_message(msg)

        cards_on_board = len(self.community_cards)

        if cards_on_board < 3: self.deal_flop()
        if cards_on_board < 4: self.deal_turn()
        if cards_on_board < 5: self.deal_river()

        self.end_round()

    def play_round(self):
        """ BUG FIX: Modified to handle all-in showdowns correctly. """
        self.reset_hand()
        if len(self.players) < 2:
            print("玩家不足，游戏结束。");
            return False

        round_start_msg = "\n" + "=" * 50 + f"\n新回合开始！庄家是: {self.players[self.dealer_index].name}\n" + "=" * 50 + "\n"
        print(round_start_msg);
        self.log_message(round_start_msg)

        self.post_blinds()
        self.deal_hole_cards()
        for p in self.players: print(f"{p.name}: {p.hand}")

        # Pre-flop
        self.current_betting_round = "Pre-flop"
        self.betting_round()
        if len(self.get_active_players()) <= 1: self.end_round(); return True
        if self.should_skip_to_showdown(): self.run_to_showdown(); return True

        # Flop
        for p in self.players: p.bet_in_round = 0
        self.current_betting_round = "Flop"
        self.deal_flop()
        print(self.get_betting_round_status())
        self.betting_round()
        if len(self.get_active_players()) <= 1: self.end_round(); return True
        if self.should_skip_to_showdown(): self.run_to_showdown(); return True

        # Turn
        for p in self.players: p.bet_in_round = 0
        self.current_betting_round = "Turn"
        self.deal_turn()
        print(self.get_betting_round_status())
        self.betting_round()
        if len(self.get_active_players()) <= 1: self.end_round(); return True
        if self.should_skip_to_showdown(): self.run_to_showdown(); return True

        # River
        for p in self.players: p.bet_in_round = 0
        self.current_betting_round = "River"
        self.deal_river()
        print(self.get_betting_round_status())
        self.betting_round()

        self.end_round()
        return True

    def end_round(self):
        print("\n" + "-" * 15 + " 回合结束 " + "-" * 15)

        # Display community cards if they were dealt
        if self.community_cards:
            print(f"\n公共牌: {' '.join(map(str, self.community_cards))}")

        self.distribute_pot()

        final_hands_msg = "\n最终亮牌:\n"
        for player in self.players:
            if not player.has_folded and player.bet_in_hand > 0:
                rank, _ = PokerHandEvaluator.evaluate_hand(player.hand, self.community_cards)
                hand_name = rank.name.replace('_', ' ').title()
                final_hands_msg += f"{player.name}: {' '.join(map(str, player.hand))} -> {hand_name}\n"
        print(final_hands_msg);
        self.log_message(final_hands_msg)

        self.players = [p for p in self.players if p.chips > 0]


def main():
    # ... [main function remains the same as your last provided version] ...
    print("欢迎来到德州扑克模拟器！")

    player_names = []
    num_players = 0
    while not 2 <= num_players <= 9:
        try:
            num_players = int(input("请输入玩家数量 (2-9): ").strip())
        except ValueError:
            print("无效输入。")

    for i in range(num_players):
        name = input(f"请输入玩家 {i + 1} 的名字: ").strip() or f"玩家 {i + 1}"
        player_names.append(name)

    try:
        initial_chips = int(input("请输入初始筹码数 (默认1000): ").strip() or "1000")
    except ValueError:
        initial_chips = 1000

    log_file = input("请输入日志文件名 (默认poker_log.txt): ").strip() or "poker_log.txt"
    game = PokerGame(player_names, initial_chips, log_file)
    with open(game.log_file, "w", encoding="utf-8") as f:
        f.write("德州扑克游戏日志\n\n")

    while True:
        if not game.play_round(): break

        chip_status = "\n当前筹码状况:\n"
        for player in game.players:
            chip_status += f"{player.name}: {player.chips} 筹码\n"
        print(chip_status);
        game.log_message(chip_status)

        if len(game.players) < 2:
            if game.players:
                print(f"\n游戏结束！最终胜者是 {game.players[0].name}！")
            else:
                print("\n游戏结束！没有赢家。")
            break

        cont = input("\n是否开始新回合？(y/n): ").strip().lower()
        if cont != 'y':
            end_game_msg = "游戏结束！感谢游玩。\n"
            print(end_game_msg);
            game.log_message(end_game_msg)
            break


if __name__ == "__main__":
    main()
