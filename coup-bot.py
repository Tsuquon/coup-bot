from operator import contains
from submission_helper.bot_battle import BotBattle
from submission_helper.state import *
from submission_helper.enums import *
from typing import Optional

class Player:
    
    def __init__(self, cards, player_id: int):
        self.cards = cards
        self.no_of_cards = 2
        self.player_id = player_id
        
    def get_data(self):
        print(self.cards, self.no_of_cards)
        


'''
Notes:
change the index on when to coup


'''

game_info: Optional[GameInfo] = None
bot_battle = BotBattle()

new_player = Player(game_info.own_cards, game_info.player_id)


# gets the closes player that is left alive in turn order
# clockwise(?) and returns their index
def get_next_alive_player():
    next_alive = (game_info.player_id + 1) % 5
    while game_info.players_cards_num[next_alive] == 0:
        next_alive = (next_alive + 1) % 5
    
    return next_alive


# Calls the appropriate function for the action requested
# of us. Could be a primary actoin, challenge, counter, 
# challenge response, or discard a card
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

# the main "play" of the game when it is our turn
def primary_action_handler():
    if game_info.balances[game_info.player_id] >= 10:
        target_player_id = get_next_alive_player()
        bot_battle.play_primary_action(PrimaryAction.Coup, target_player_id)
        
    if game_info.balances[game_info.player_id] >= 3:
        target_player_id = get_next_alive_player()
        bot_battle.play_primary_action(PrimaryAction.Assassinate, target_player_id)
        
    else:
        bot_battle.play_primary_action(PrimaryAction.Income)

# TODO: add logic here for when we want to counter
def counter_action_handler():
    bot_battle.play_counter_action(CounterAction.NoCounterAction)

# TODO: add logic here for when we want to call someone's bluff
def challenge_action_handler():
    bot_battle.play_challenge_action(ChallengeAction.NoChallenge)

# TODO: is this the part that asks us if we're lying or not?
def challenge_response_handler():
    bot_battle.play_challenge_response(0)

# TODO: discards the card of least value to prepare for endgame
# strategy in the following order
# Captain > Assassin > Contessa > Duke > Ambassador
def discard_choice_handler():
    if contains(game_info.own_cards, Character.Ambassador):
        # how do we know which index the Ambassador card is in?
        bot_battle.play_discard_choice(1) # discard Ambassador instead of Assassin or Captain
    
    elif contains(game_info.own_cards, Character.Duke):
        bot_battle.play_discard_choice(1)# discard Duke instead of Assassin or Captain

    elif contains(game_info.own_cards, Character.Contessa):
        bot_battle.play_discard_choice(1) # discard Contessa instead of Assassin or Captain

    elif contains(game_info.own_cards, Character.Assassin):
        bot_battle.play_discard_choice(1) # discard Assassin instead of Assassin or Captain

    else:
        bot_battle.play_discard_choice(0) # discard whatever else instead of Captain

# Gets fresh data on every instance and checks if we need to 
# perform a move
if __name__ == "__main__":
    while True:
        game_info = bot_battle.get_game_info()
        move_controller(game_info.requested_move)