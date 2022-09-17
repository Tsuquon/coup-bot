from ast import Num
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
        print("Richest is", get_richest_alive(), flush = True) 
    
    except UnboundLocalError as e:
        print("Error with new player", flush=True)
        print(e, flush=True)
    
def get_previous_action_in_turn() -> Action:
    return list(game_info.history[-1].values())[-1]

def get_richest_alive():
    #Not sure what to do if richest ppl = same number of coins 
    list_2 = new_board.get_balance().copy()
    list_2.sort()
    if list_2[-1] == game_info.player_id and list_2[-2] != list_2[-1]:
        return list_2.index(list_2[-2])
    
    else:
        return list_2.index(list_2[-1])
        
        
# gets the closes player that is left alive in turn order
# clockwise(?) and returns their index
def get_next_alive_player():
    next_alive = (game_info.player_id + 1) % 5
    while game_info.players_cards_num[next_alive] == 0:
        next_alive = (next_alive + 1) % 5
    
    return next_alive

# gets the closest player on the anticlockwise direction and returns index
def get_left_alive_player():
    left_alive = (game_info.player_id - 1) % 5
    while game_info.players_cards_num[left_alive] == 0:
        left_alive = (left_alive - 1 )% 5
    return left_alive



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
    # Bot does nothing with captain and ambassador, but takes income? No wonder its losing!
    # If its ambassador swap with assassin
    
    print(new_board.get_balance()[game_info.player_id] , flush = True)
    print(new_board.get_balance()[game_info.player_id] >= 10, flush = True)
    if new_board.get_balance()[game_info.player_id] >= 10:
        print("this runs", flush = True)
        bot_battle.play_primary_action(PrimaryAction.Coup, get_richest_alive())
    
    elif game_info.balances[game_info.player_id] >= 3 and assassin_challenged == False and new_board.get_num_alive_players() == 2:
        bot_battle.play_primary_action(PrimaryAction.Assassinate, get_next_alive_player())
        
    elif game_info.balances[game_info.player_id] >= 3 and game_info.balances[game_info.player_id] >= 3 and assassin_challenged == False: # TODO: If player gets challenged after assassinate, do something
        bot_battle.play_primary_action(PrimaryAction.Assassinate, get_left_alive_player())
    
    elif duke_challenged == False: # TODO: If player gets challenged after tax, change these to true
        bot_battle.play_primary_action(PrimaryAction.Tax)
    
    # elif Character.Ambassador in game_info.own_cards: # Should trade out cards, but how?
    #     if assassin_challenged == True:
    #         pass
    
    elif game_info.balances[game_info.player_id] >= 7 and new_board.get_num_alive_players() != 3:
        target_player_id = get_left_alive_player()
        bot_battle.play_primary_action(PrimaryAction.Coup, target_player_id)
        
    else:
        target_player_id = get_richest_alive()
        if new_board.get_balance()[target_player_id] == 0:
            bot_battle.play_primary_action(PrimaryAction.Income)
        else:
            bot_battle.play_primary_action(PrimaryAction.Steal, target_player_id)

        
# TODO: add logic here for when we want to counter
def counter_action_handler():
    primary_action = game_info.history[-1][ActionType.PrimaryAction].action
    # first command is what other players do
    
    if primary_action == PrimaryAction.Assassinate and new_player.no_of_cards == 1:
        bot_battle.play_counter_action(CounterAction.BlockAssassination)
    
    if primary_action == PrimaryAction.Assassinate and Character.Contessa in (game_info.own_cards) :
        bot_battle.play_counter_action(CounterAction.BlockAssassination)

    elif primary_action == PrimaryAction.ForeignAid and Character.Duke in (game_info.own_cards):
        bot_battle.play_counter_action(CounterAction.BlockForeignAid)

    elif primary_action == PrimaryAction.Steal and Character.Captain in (game_info.own_cards):
            bot_battle.play_counter_action(CounterAction.BlockStealingAsCaptain)
    
    elif primary_action == PrimaryAction.Steal and Character.Ambassador in (game_info.own_cards):
        bot_battle.play_counter_action(CounterAction.BlockStealingAsAmbassador)  


    
    else:
        bot_battle.play_counter_action(CounterAction.NoCounterAction)



# TODO: We challenge someone
def challenge_action_handler():
    primary_action = game_info.history[-1][ActionType.PrimaryAction].action
   
    if new_player.no_of_cards == 1 and Character.Contessa not in game_info.own_cards and primary_action == PrimaryAction.Assassinate:
        bot_battle.play_challenge_action(ChallengeAction.Challenge)
    
    bot_battle.play_challenge_action(ChallengeAction.NoChallenge)

# TODO: We get challenged
def challenge_response_handler():
    previous_action = get_previous_action_in_turn()

    reveal_card_index = None

    # Challenge was primary action
    if previous_action.action_type == ActionType.PrimaryAction:
        primary_action = game_info.history[-1][ActionType.PrimaryAction].action

        # If we have the card we used, lets reveal it
        if primary_action == PrimaryAction.Assassinate:
            reveal_card_index = game_info.own_cards.index(Character.Assassin)
        elif primary_action == PrimaryAction.Exchange:
            reveal_card_index = game_info.own_cards.index(Character.Ambassador)
        elif primary_action == PrimaryAction.Steal:
            reveal_card_index = game_info.own_cards.index(Character.Captain)
        elif primary_action == PrimaryAction.Tax:
            reveal_card_index = game_info.own_cards.index(Character.Duke)

        # Challenge was counter action
    elif previous_action.action_type == ActionType.CounterAction:
        counter_action = game_info.history[-1][ActionType.CounterAction].action

        # If we have the card we used, lets reveal it
        if counter_action == CounterAction.BlockAssassination:
            reveal_card_index = game_info.own_cards.index(Character.Contessa)
        elif counter_action == CounterAction.BlockStealingAsAmbassador:
            reveal_card_index = game_info.own_cards.index(Character.Ambassador)
        elif counter_action == CounterAction.BlockStealingAsCaptain:
            reveal_card_index = game_info.own_cards.index(Character.Captain)
        elif counter_action == CounterAction.BlockForeignAid:
            reveal_card_index = game_info.own_cards.index(Character.Duke)
        
        # If we lied, let's reveal our first card
    if reveal_card_index == None or reveal_card_index == -1:
        reveal_card_index = 0

    bot_battle.play_challenge_response(reveal_card_index)

# TODO: discards the card of least value to prepare for endgame
# strategy in the following order
# Captain > Assassin > Contessa > Duke > Ambassador
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
    else:
       
        if len(game_info.own_cards) == 1:
            bot_battle.play_discard_choice(0)
        
        elif len(game_info.own_cards) == 2:
            if contains(game_info.own_cards, Character.Ambassador):
                # how do we know which index the Ambassador card is in?
                bot_battle.play_discard_choice(game_info.own_cards.index(Character.Ambassador)) # discard Ambassador instead of Assassin or Captain
            
            elif contains(game_info.own_cards, Character.Duke):
                bot_battle.play_discard_choice(game_info.own_cards.index(Character.Duke))# discard Duke instead of Assassin or Captain

            elif contains(game_info.own_cards, Character.Contessa):
                bot_battle.play_discard_choice(game_info.own_cards.index(Character.Contessa)) # discard Contessa instead of Assassin or Captain

            elif contains(game_info.own_cards, Character.Assassin):
                bot_battle.play_discard_choice(game_info.own_cards.index(Character.Assassin)) # discard Assassin instead of Assassin or Captain

            else:
                bot_battle.play_discard_choice(0) # discard whatever else instead of Captain
                
                
# Gets fresh data on every instance and checks if we need to 
# perform a move
if __name__ == "__main__":   
    
    while True:
        game_info = bot_battle.get_game_info()
        personal_function()
        move_controller(game_info.requested_move)


# Notes:
# If assassinating and they block with contessa, shouldn't try and assassinate them again
# If one card, they block, then challenge, and if they are about to coup us.
