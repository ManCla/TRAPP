from app.adaptation.Strategy import Strategy

class NoAdaptation(Strategy):

    def monitor(self):
        pass

    def analyze(self, utilizations):
        pass

    def plan(self, overloaded_streets):
        pass

    def execute(self, avoid_streets_signal):
        pass