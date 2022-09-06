from submission_helper.bot_battle import BotBattle
from submission_helper.state import *
from submission_helper.enums import *
from typing import Optional

class Player:
    
    def __init__(self, cards, no_of_cards):
        self.cards = cards
        self.no_of_cards = no_of_cards
        self.get_data()
        
    def get_data(self):
        print(self.cards, self.no_of_cards)
        




'''
Notes:
change the index on when to coup


'''

game_info: Optional[GameInfo] = None
bot_battle = BotBattle()

our_bot = Player(game_info.own_cards, game_info.players_cards_num)


def get_next_alive_player():
    next_alive = (game_info.player_id + 1) % 5
    while game_info.players_cards_num[next_alive] == 0:
        next_alive = (next_alive + 1) % 5
    
    return next_alive


def move_controller(requested_move: RequestedMove):
    if requested_move == RequestedMove.PrimaryAction:
        primary_action_handler()

    elif requested_move == RequestedMove.CounterAction:
        counter_action_handler()

    elif requested_move == RequestedMove.ChallengeAction:
        challenge_action_handler()

    elif requested_move == RequestedMove.ChallengeResponse:
        challenge_response_handler()

    elif requested_move == RequestedMove.DiscardChoice:
        discard_choice_handler()

    else:
        return Exception(f'Unknown requested move: {requested_move}')


def primary_action_handler():
    if game_info.balances[game_info.player_id] >= 10:
        target_player_id = get_next_alive_player()
        bot_battle.play_primary_action(PrimaryAction.Coup, target_player_id)
    else:
        bot_battle.play_primary_action(PrimaryAction.Income)


def counter_action_handler():
    bot_battle.play_counter_action(CounterAction.NoCounterAction)


def challenge_action_handler():
    bot_battle.play_challenge_action(ChallengeAction.NoChallenge)


def challenge_response_handler():
    bot_battle.play_challenge_response(0)


def discard_choice_handler():
    bot_battle.play_discard_choice(0)


if __name__ == "__main__":
    while True:
        game_info = bot_battle.get_game_info()
        move_controller(game_info.requested_move)