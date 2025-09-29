import random
from typing import List, Dict, Tuple, Optional
from enum import Enum


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
        rank_str = self.rank.name[0] if self.rank.value > 10 else str(self.rank.value)
        return f"{rank_str}{self.suit.value}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other):
        return self.rank.value < other.rank.value


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
        # Sort cards by rank in descending order
        all_cards.sort(key=lambda c: c.rank.value, reverse=True)

        # Get ranks and suits
        ranks = [card.rank.value for card in all_cards]
        suits = [card.suit for card in all_cards]

        # Count rank occurrences
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1

        # Sort rank counts by frequency (descending), then by rank (descending)
        sorted_rank_counts = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

        is_flush = len(set(suits)) == 1
        unique_ranks = sorted(list(set(ranks)), reverse=True)
        is_straight = False
        if len(unique_ranks) >= 5:
            # Check for regular straight
            for i in range(len(unique_ranks) - 4):
                if unique_ranks[i] - unique_ranks[i + 4] == 4:
                    is_straight = True
                    straight_high = unique_ranks[i]
                    break
            # Check for wheel straight (A-2-3-4-5)
            if 14 in unique_ranks and 5 in unique_ranks and 4 in unique_ranks and 3 in unique_ranks and 2 in unique_ranks:
                is_straight = True
                straight_high = 5

        # Royal Flush
        if is_straight and is_flush:
            if straight_high == 14:  # Ace high straight
                return HandRank.ROYAL_FLUSH, [14]
            else:
                return HandRank.STRAIGHT_FLUSH, [straight_high]

        # Four of a Kind
        if sorted_rank_counts[0][1] == 4:
            four_rank = sorted_rank_counts[0][0]
            kicker = next((rank for rank, count in sorted_rank_counts if rank != four_rank), None)
            return HandRank.FOUR_OF_A_KIND, [four_rank, kicker] if kicker else [four_rank]

        # Full House
        if sorted_rank_counts[0][1] == 3 and len(sorted_rank_counts) > 1 and sorted_rank_counts[1][1] >= 2:
            three_rank = sorted_rank_counts[0][0]
            two_rank = sorted_rank_counts[1][0]
            return HandRank.FULL_HOUSE, [three_rank, two_rank]

        # Flush
        if is_flush:
            flush_ranks = [rank for rank in unique_ranks][:5]
            return HandRank.FLUSH, flush_ranks

        # Straight
        if is_straight:
            return HandRank.STRAIGHT, [straight_high]

        # Three of a Kind
        if sorted_rank_counts[0][1] == 3:
            three_rank = sorted_rank_counts[0][0]
            kickers = []
            for rank, count in sorted_rank_counts:
                if rank != three_rank:
                    kickers.extend([rank] * min(count, 2))
                if len(kickers) >= 2:
                    break
            return HandRank.THREE_OF_A_KIND, [three_rank] + kickers[:2]

        # Two Pair
        if sorted_rank_counts[0][1] == 2 and len(sorted_rank_counts) > 1 and sorted_rank_counts[1][1] == 2:
            pair1_rank = sorted_rank_counts[0][0]
            pair2_rank = sorted_rank_counts[1][0]
            kicker = next((rank for rank, count in sorted_rank_counts if rank not in [pair1_rank, pair2_rank]), None)
            return HandRank.TWO_PAIR, [pair1_rank, pair2_rank, kicker] if kicker else [pair1_rank, pair2_rank]

        # Pair
        if sorted_rank_counts[0][1] == 2:
            pair_rank = sorted_rank_counts[0][0]
            kickers = []
            for rank, count in sorted_rank_counts:
                if rank != pair_rank:
                    kickers.extend([rank] * min(count, 1))
                if len(kickers) >= 3:
                    break
            return HandRank.PAIR, [pair_rank] + kickers[:3]

        # High Card
        return HandRank.HIGH_CARD, unique_ranks[:5]


class Player:
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.current_bet = 0
        self.is_active = True
        self.has_folded = False
        self.is_all_in = False

    def reset_for_round(self):
        self.hand = []
        self.current_bet = 0
        self.is_active = True
        self.has_folded = False
        self.is_all_in = False

    def bet(self, amount: int) -> int:
        actual_bet = min(amount, self.chips)
        self.chips -= actual_bet
        self.current_bet += actual_bet
        if self.chips == 0:
            self.is_all_in = True
        return actual_bet

    def __repr__(self):
        status = " (已弃牌)" if self.has_folded else " (已全下)" if self.is_all_in else ""
        return f"{self.name}: 手牌{self.hand}, 筹码{self.chips}, 当前下注{self.current_bet}{status}"


class PokerGame:
    def __init__(self, player_names: List[str], initial_chips: int = 1000):
        self.players = [Player(name, initial_chips) for name in player_names]
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_betting_round = 0  # 0=Pre-flop, 1=Flop, 2=Turn, 3=River
        self.current_player_index = 0
        self.small_blind_amount = 10
        self.big_blind_amount = 20
        self.dealer_index = 0
        self.min_raise = self.big_blind_amount

    def reset_game(self):
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_betting_round = 0
        self.min_raise = self.big_blind_amount
        for player in self.players:
            player.reset_for_round()
        self.dealer_index = (self.dealer_index + 1) % len(self.players)

    def deal_hole_cards(self):
        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.deal_card())

    def deal_flop(self):
        self.deck.deal_card()  # Burn card
        for _ in range(3):
            self.community_cards.append(self.deck.deal_card())

    def deal_turn(self):
        self.deck.deal_card()  # Burn card
        self.community_cards.append(self.deck.deal_card())

    def deal_river(self):
        self.deck.deal_card()  # Burn card
        self.community_cards.append(self.deck.deal_card())

    def post_blinds(self):
        sb_index = (self.dealer_index + 1) % len(self.players)
        bb_index = (self.dealer_index + 2) % len(self.players)

        sb_player = self.players[sb_index]
        bb_player = self.players[bb_index]

        sb_bet = sb_player.bet(self.small_blind_amount)
        bb_bet = bb_player.bet(self.big_blind_amount)

        self.pot += sb_bet + bb_bet
        self.min_raise = self.big_blind_amount

        print(f"{sb_player.name} 下小盲注 {sb_bet}")
        print(f"{bb_player.name} 下大盲注 {bb_bet}")
        print(f"当前底池: {self.pot}\n")

    def get_active_players(self) -> List[Player]:
        return [p for p in self.players if p.is_active and not p.has_folded]

    def get_betting_round_status(self) -> str:
        status = f"\n--- {['Pre-flop', 'Flop', 'Turn', 'River'][self.current_betting_round]} ---\n"
        status += f"公共牌: {self.community_cards}\n"
        status += f"当前底池: {self.pot}\n"
        for player in self.players:
            status += f"{player}\n"
        return status

    def betting_round(self):
        active_players = self.get_active_players()
        if len(active_players) <= 1:
            return  # Only one player left, no betting needed

        current_bet = max(p.current_bet for p in self.players)
        last_raiser_index = -1
        num_active_players = len(active_players)
        bets_made_in_round = 0

        # First player to act
        self.current_player_index = (self.dealer_index + 1) % len(self.players)
        while self.players[self.current_player_index].has_folded or self.players[self.current_player_index].is_all_in:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

        while True:
            player = self.players[self.current_player_index]
            if player.has_folded or player.is_all_in:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                continue

            print(f"\n轮到 {player.name} 操作")
            print(f"当前下注: {current_bet}, 您已下注: {player.current_bet}")

            # Determine valid actions
            valid_actions = ["fold", "call"]
            if player.chips > 0:
                if current_bet == player.current_bet:
                    valid_actions.append("check")
                else:
                    valid_actions.append("raise")
            else:
                # Player is all-in, can only fold or call (which is free if current_bet <= player.current_bet)
                pass

            print(f"可用操作: {valid_actions}")

            # In a real game, this would be user input. For simulation, we'll define a simple strategy or allow input.
            # Here, we'll prompt for action
            action_input = input("请输入操作 (fold/check/call/raise): ").strip().lower()
            while action_input not in valid_actions:
                action_input = input(f"无效操作。请选择: {valid_actions}: ").strip().lower()

            if action_input == "fold":
                player.has_folded = True
                player.is_active = False
                num_active_players -= 1
                if num_active_players <= 1:
                    break

            elif action_input == "check":
                print(f"{player.name} 过牌")
                # No action needed, move to next player

            elif action_input == "call":
                call_amount = current_bet - player.current_bet
                actual_call = player.bet(call_amount)
                self.pot += actual_call
                print(f"{player.name} 跟注 {actual_call}")
                if player.chips == 0:
                    print(f"{player.name} 已全下！")

            elif action_input == "raise":
                min_raise_amount = max(self.min_raise, current_bet - player.current_bet + self.big_blind_amount)
                max_raise_amount = player.chips + player.current_bet
                print(f"最小加注额: {min_raise_amount}, 最大可加注到: {max_raise_amount}")
                try:
                    raise_amount = int(input(f"请输入加注额 (至少 {min_raise_amount}): "))
                    while raise_amount < min_raise_amount or raise_amount > max_raise_amount:
                        raise_amount = int(
                            input(f"加注额无效。请输入 {min_raise_amount} 到 {max_raise_amount} 之间的数: "))
                except ValueError:
                    print("输入无效，使用最小加注额")
                    raise_amount = min_raise_amount

                actual_raise = player.bet(raise_amount - player.current_bet)
                self.pot += actual_raise
                current_bet = player.current_bet
                last_raiser_index = self.current_player_index
                self.min_raise = raise_amount - (current_bet - actual_raise)
                print(f"{player.name} 加注到 {current_bet} (净加注 {actual_raise})")
                bets_made_in_round += 1
                if player.chips == 0:
                    print(f"{player.name} 已全下！")

            self.current_player_index = (self.current_player_index + 1) % len(self.players)

            # Check if betting round is over
            # Betting ends when all active players have matched the current bet
            active_players_in_round = [p for p in self.get_active_players() if not p.has_folded]
            if all(p.current_bet == current_bet for p in active_players_in_round):
                if last_raiser_index == -1 or self.current_player_index == last_raiser_index:
                    # All players have called the last raise (or checked)
                    break

        # Reset current bets for next round, except for all-in players
        for p in self.players:
            if not p.is_all_in:
                p.current_bet = 0

    def determine_winner(self) -> List[Tuple[Player, HandRank, List[int], str]]:
        active_players = self.get_active_players()
        if len(active_players) == 1:
            winner = active_players[0]
            rank, ranks = PokerHandEvaluator.evaluate_hand(winner.hand, self.community_cards)
            hand_name = rank.name.replace('_', ' ').title()
            return [(winner, rank, ranks, hand_name)]

        results = []
        for player in active_players:
            rank, ranks = PokerHandEvaluator.evaluate_hand(player.hand, self.community_cards)
            hand_name = rank.name.replace('_', ' ').title()
            results.append((player, rank, ranks, hand_name))

        # Sort by rank, then by kicker values
        results.sort(key=lambda x: (x[1].value, x[2]), reverse=True)

        # Check for ties
        max_rank = results[0][1].value
        max_ranks_list = results[0][2]
        winners = []
        for res in results:
            if res[1].value == max_rank:
                # Compare kickers
                if res[2] == max_ranks_list:
                    winners.append(res)
                else:
                    # Need more complex kicker comparison
                    is_tie = True
                    min_len = min(len(max_ranks_list), len(res[2]))
                    for i in range(min_len):
                        if max_ranks_list[i] != res[2][i]:
                            is_tie = False
                            if res[2][i] > max_ranks_list[i]:
                                winners = [res]
                                max_ranks_list = res[2]
                            break
                    if is_tie and len(res[2]) == len(max_ranks_list):
                        winners.append(res)
                    elif not is_tie and res[1].value == max_rank and res[2][0] > max_ranks_list[0]:
                        winners = [res]
                        max_ranks_list = res[2]
            else:
                break  # Lower rank, stop checking

        return winners

    def distribute_pot(self, winners: List[Tuple[Player, HandRank, List[int], str]]):
        if not winners:
            print("没有胜者！")
            return

        if len(winners) == 1:
            winner, rank, ranks, hand_name = winners[0]
            print(f"\n胜者: {winner.name} - {hand_name} ({' '.join(map(str, winner.hand))})")
            winner.chips += self.pot
            print(f"{winner.name} 获得底池 {self.pot} 筹码！")
        else:
            print(f"\n平局！以下玩家获胜:")
            split_pot = self.pot // len(winners)
            for winner, rank, ranks, hand_name in winners:
                print(f"- {winner.name} - {hand_name} ({' '.join(map(str, winner.hand))})")
                winner.chips += split_pot
                print(f"  {winner.name} 获得 {split_pot} 筹码！")
            if self.pot % len(winners) > 0:
                # Handle remainder chips if pot doesn't divide evenly
                remainder = self.pot % len(winners)
                for i in range(remainder):
                    winners[i][0].chips += 1
                print(f"剩余 {remainder} 筹码分配给前几位赢家")

    def play_round(self):
        print("\n" + "=" * 50)
        print("新回合开始！")
        print("=" * 50)
        self.reset_game()
        self.deal_hole_cards()
        self.post_blinds()

        # Pre-flop betting
        print(self.get_betting_round_status())
        self.betting_round()

        # Check if only one player remains
        if len(self.get_active_players()) <= 1:
            self.end_round()
            return

        # Flop
        self.current_betting_round = 1
        self.deal_flop()
        print(self.get_betting_round_status())
        self.betting_round()

        if len(self.get_active_players()) <= 1:
            self.end_round()
            return

        # Turn
        self.current_betting_round = 2
        self.deal_turn()
        print(self.get_betting_round_status())
        self.betting_round()

        if len(self.get_active_players()) <= 1:
            self.end_round()
            return

        # River
        self.current_betting_round = 3
        self.deal_river()
        print(self.get_betting_round_status())
        self.betting_round()

        self.end_round()

    def end_round(self):
        active_players = self.get_active_players()
        if len(active_players) > 1:
            winners = self.determine_winner()
            self.distribute_pot(winners)
        elif len(active_players) == 1:
            # Only one player didn't fold
            winner = active_players[0]
            print(f"\n{winner.name} 是唯一未弃牌的玩家，赢得底池 {self.pot}！")
            winner.chips += self.pot
        else:
            # This shouldn't happen in normal play
            print("回合结束，无活跃玩家。")

        # Show final hands if more than one player was active at the end
        if len(self.get_active_players()) > 0:
            print("\n最终手牌:")
            for player in self.players:
                if not player.has_folded:
                    rank, ranks = PokerHandEvaluator.evaluate_hand(player.hand, self.community_cards)
                    hand_name = rank.name.replace('_', ' ').title()
                    print(f"{player.name}: {' '.join(map(str, player.hand))} - {hand_name}")
            print(f"公共牌: {' '.join(map(str, self.community_cards))}")


def main():
    print("欢迎来到德州扑克模拟器！")
    print("游戏将包含3名玩家，你可以自定义他们的操作。")

    player_names = []
    for i in range(3):
        name = input(f"请输入玩家 {i + 1} 的名字: ").strip()
        if not name:
            name = f"玩家 {i + 1}"
        player_names.append(name)

    try:
        initial_chips = int(input("请输入初始筹码数 (默认1000): ").strip() or "1000")
    except ValueError:
        initial_chips = 1000

    game = PokerGame(player_names, initial_chips)

    while True:
        game.play_round()

        print("\n当前筹码状况:")
        for player in game.players:
            print(f"{player.name}: {player.chips} 筹码")

        cont = input("\n是否开始新回合？(y/n): ").strip().lower()
        if cont != 'y':
            print("游戏结束！感谢游玩。")
            break


if __name__ == "__main__":
    main()



