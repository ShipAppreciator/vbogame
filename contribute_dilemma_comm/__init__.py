
from otree.api import *
import random
c = cu

class C(BaseConstants):
    NAME_IN_URL = 'contribute_dilemma_comm'
    PLAYERS_PER_GROUP = 9
    NUM_ROUNDS = 10
    NUMCONS = 6
    NUM_OTHER_PLAYERS = 8
    GENERAL_BENEFIT = cu(100)
    ENDOWMENT = cu(0)
    INSTRUCTIONS_TEMPLATE = 'contribute_dilemma_comm/instructions.html'
class Subsession(BaseSubsession):
    pass
    
class Group(BaseGroup):
    num_contributes = models.IntegerField()
def set_payoffs(group: Group):
    players = group.get_players()
    group.num_contributes = sum([p.contribute for p in players])
    if group.num_contributes >= C.NUMCONS:
        baseline_amount = C.GENERAL_BENEFIT
    else:
        baseline_amount = cu(0)
    for p in players:
        p.payoff = baseline_amount
        if p.contribute:
            p.payoff -= p.cost
        p.earnings+=p.payoff
                # Update cumulative earnings in participant.vars
        cumulative_earnings = p.participant.vars.get('cumulative_earnings', 0)
        p.participant.vars['cumulative_earnings'] = cumulative_earnings + p.payoff
def vol_logic(group:Group):
    vol_players = [p for p in group.get_players() if p.volunteer]
    if len(vol_players) >= C.NUMCONS:
        voluntolds = random.sample(vol_players, C.NUMCONS)
        for p in group.get_players():
            if p in voluntolds:
                p.voluntold = True
            else:
                p.voluntold = False
    else:
        for p in group.get_players():
            p.voluntold = False
            
        
class Player(BasePlayer):
    contribute = models.BooleanField(doc='Whether player contributes', label='Do you wish to contribute?')
    volunteer = models.BooleanField(doc='Whether player volunteers', label = 'Do you wish to volunteer? Remember that this decision is non binding.')
    cost = models.CurrencyField()
    earnings = models.CurrencyField()
    voluntold = models.BooleanField()
    def total_earnings(self):
        prior_app_earnings = self.participant.vars.get('cumulative_earnings', 0)
        current_earnings = self.earnings or 0
        return prior_app_earnings
    def total_earnings_in_dollars(self):
        return self.total_earnings() * 0.01  # Convert points to dollars
class Introduction(Page):
    form_model = 'player'
    def is_displayed(self):
        return self.round_number == 1
class Volunteer(Page):
    form_model = 'player'
    form_fields = ['volunteer']
class SugWaitPage(WaitPage):
    after_all_players_arrive = vol_logic
class Suggestion(Page):
    pass
class Decision(Page):
    form_model = 'player'
    form_fields = ['contribute']
class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
class Results(Page):
    form_model = 'player'
class End(Page):
    form_model = 'player'
    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS
    
def creating_session(subsession):
    for player in subsession.get_players():
        player.earnings = C.ENDOWMENT
        # Assign a random cost for this round
        player.cost = cu(random.randint(1, 120))
        
page_sequence = [Introduction, Volunteer, SugWaitPage, Suggestion, Decision, ResultsWaitPage, Results, End]
