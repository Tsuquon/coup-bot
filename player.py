class Player:
    
    def __init__(self, cards, no_of_cards):
        self.cards = cards
        self.no_of_cards = no_of_cards
        get_data()
        
    def get_data(self):
        print(self.cards, self.no_of_cards)
        