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
        return self.cards, self.no_of_cards, self.player_id
    
    def update_data(self, cards, no_of_cards):
        self.cards = cards
        self.no_of_cards = no_of_cards
        
class Board:
    
    def __init__(self, balance, current_cards):
        self.balance = balance # List of int
        self.current_cards = current_cards # List of int

    def get_balance(self):
        return self.balance
    
    def get_current_cards(self):
        return self.current_cards
    
    def update_data(self, balance, current_cards):
        self.balance = balance
        self.current_cards = current_cards
        
    def get_num_alive_players(self):
        num_alive = 5
        for i in self.get_current_cards():
            if i == 0:
                num_alive -= 1
        
        return num_alive
        
'''
Notes:
change the index on when to coup
'''

game_info: Optional[GameInfo] = None
bot_battle = BotBattle()
run_once = False
new_player = None
new_board = None
duke_challenged = False
assassin_challenged = False

is_last_counter_block_as_cap = True

def personal_function():
    global run_once, new_player, new_board
    
    if run_once == False:
        new_player = Player(game_info.own_cards, game_info.player_id)
        new_board  = Board(game_info.balances, game_info.players_cards_num) 
        run_once = True
    
    new_player.update_data(game_info.own_cards, game_info.players_cards_num[game_info.player_id])
    new_board.update_data(game_info.balances, game_info.players_cards_num)
 
    try:
        print("player info:", new_player.get_data(), flush=True)
        print("other player balance", new_board.get_balance(), flush=True)
        print("other players card num", new_board.get_current_cards(), flush=True)
        print("Richest is", get_next_alive_player(), flush = True) 
    
    except UnboundLocalError as e:
        print("Error with new player", flush=True)
        print(e, flush=True)

def get_anticlockwise_alive_player():
    left_alive = (game_info.player_id - 1) % 5
    while game_info.players_cards_num[left_alive] == 0:
        left_alive = (left_alive - 1 )% 5
    return left_alive

def get_next_alive_player():
    next_alive = (game_info.player_id + 1) % 5
    while game_info.players_cards_num[next_alive] == 0:
        next_alive = (next_alive + 1) % 5
    
    return next_alive

def get_richest_alive():
    ls = new_board.get_balance()
    ls[game_info.player_id] = -1
    richest = new_board.get_balance().index(max(new_board.get_balance()))
    
    while new_board.get_current_cards()[richest] == 0:
        ls[richest] = -1
        richest = new_board.get_balance().index(max(new_board.get_balance()))
        
    print("Richest is", richest, flush = True)

    return richest

    
 
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
    if not contains(game_info.own_cards, Character.Captain):
        bot_battle.play_primary_action(PrimaryAction.Exchange)
           
    elif game_info.balances[game_info.player_id] >= 7:
        target_player_id = get_next_alive_player()
        bot_battle.play_primary_action(PrimaryAction.Coup, target_player_id)
    else:
        target_player_id = get_anticlockwise_alive_player() 
        if new_board.get_balance()[target_player_id] == 0:
            bot_battle.play_primary_action(PrimaryAction.Income)
        else:
            bot_battle.play_primary_action(PrimaryAction.Steal, target_player_id)


# Launches a counter action depending on what the last primary action was
# This tests whether reading the history is functional and whether counter
def counter_action_handler():
    global is_last_counter_block_as_cap
    primary_action = game_info.history[-1][ActionType.PrimaryAction].action

    if primary_action == PrimaryAction.Assassinate:
        bot_battle.play_counter_action(CounterAction.BlockAssassination)

    elif primary_action == PrimaryAction.ForeignAid:
        bot_battle.play_counter_action(CounterAction.BlockForeignAid)

    elif primary_action == PrimaryAction.Steal:
        if is_last_counter_block_as_cap:
            bot_battle.play_counter_action(CounterAction.BlockStealingAsAmbassador) 
        else:
            bot_battle.play_counter_action(CounterAction.BlockStealingAsCaptain)

        is_last_counter_block_as_cap = not is_last_counter_block_as_cap
    
    else:
        bot_battle.play_counter_action(CounterAction.NoCounterAction)
        

def challenge_action_handler():
    bot_battle.play_challenge_action(ChallengeAction.NoChallenge)


def challenge_response_handler():
    bot_battle.play_challenge_response(0)


def discard_choice_handler():
    primary_action = game_info.history[-1][ActionType.PrimaryAction]


    if primary_action.action == PrimaryAction.Exchange and primary_action.successful: 
        print(game_info.own_cards, flush=True)
        if contains(game_info.own_cards, Character.Captain):
            want_index = game_info.own_cards.index(Character.Captain)
            ls= []
            for i in range(game_info.own_cards):
                if i != want_index:
                    ls.append(i)

            bot_battle.play_discard_choice(ls[1])
            bot_battle.play_discard_choice(ls[0])
    
    
    elif contains(game_info.own_cards, Character.Captain):
        want_index = game_info.own_cards.index(Character.captain)
        ls = []
        for i in range(game_info.own_cards):
            if i != want_index:
                ls.append(i)
        botbattle.play_discard_choice(0)

    else:
        bot_battle.play_discard_choice(0)


if __name__ == "__main__":
    while True:
        game_info = bot_battle.get_game_info()
        personal_function()
        move_controller(game_info.requested_move)
