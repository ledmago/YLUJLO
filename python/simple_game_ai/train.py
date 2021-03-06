import random
from model import *
from game import *
from utils import *

def train(state_size, num_actions, exploration_rate=.05, discount_rate=.9, lr=.1, num_epochs=10, use_critic=False):
    # agent and environment
    actor = Actor(state_size, num_actions).to(device)
    actor_optimizer = torch.optim.SGD(actor.parameters(), lr=lr)
    critic = Critic(state_size, num_actions).to(device)
    critic_loss = nn.MSELoss()
    critic_optimizer = torch.optim.SGD(critic.parameters(), lr=lr)
    
    memory = [] # [(state, action index, next state, reward), ...]

    def batch_action(action):
        return torch.tensor([action]).long().to(device)

    def update_critic(state, action_index, nextState, reward):
        value = critic(state, action_index)

        # find best next move according to critic
        max_next_action = batch_action(0)
        max_next_value = critic(nextState, batch_action(0))
        for next_action in range(1, num_actions):
            next_action = batch_action(next_action)
            next_value = critic(nextState, next_action)
            if next_value > max_next_value:
                max_next_action = next_action
                max_next_value = next_value

        # update critic
        critic.zero_grad()
        truth = max_next_value * discount_rate + reward
        loss = critic_loss(value, truth)
        loss.backward()
        critic_optimizer.step()
        return loss.item()

    def run_episode(show=False):
        '''
        play the game and remember what happened
        '''
        game = Game()
        # playing vars
        state = state_to_tensor(game.return_state())
        reward = 0
        didWin = False

        actor_losses = []
        critic_losses = []

        for t in range(20):
            if show:
                print()
                print(game)
            # play an episode
            if didWin:
                break
            action_logprob, action_index = actor.choose_action(state)
            should_explore = random.random() < exploration_rate
            if should_explore:
                # sometimes, do a random action just to see what happens
                action_logprob, action_index = torch.tensor(1 / num_actions).to(device), batch_action(random.randint(0, num_actions-1))
            # observe next state and collect reward
            reward, nextState, didWin = game.move_player(action_index)
            nextState = state_to_tensor(nextState)
            value = critic(state, action_index)
            
            critic_loss = update_critic(state, action_index, nextState, reward)
            critic_losses.append(critic_loss)

            if not should_explore:
                # backprop rewards to actor
                actor.zero_grad()
                logprob = action_logprob
                if use_critic:
                    score = logprob * value
                else:
                    score = logprob * reward
                loss = -score
                # if reward >= 1:
                #     print(state)
                #     print(reward, action_index.item(), loss.item(), logprob.item(), value.item())
                actor_losses.append(loss.item())
                loss.backward()
                actor_optimizer.step()
            # remember what just happened
            memory.append((state, action_index, nextState, reward))
            # update state
            state = nextState
        avg_actor_loss = sum(actor_losses) / len(actor_losses)
        avg_critic_loss = sum(critic_losses) / len(critic_losses)
        return avg_actor_loss, avg_critic_loss

    def train_on_memory():
        for state, action_index, nextState, reward in random.sample(memory, min(len(memory), 10)):
            update_critic(state, action_index, nextState, reward)

    for epoch in range(num_epochs):
        avg_actor_loss, avg_critic_loss = run_episode()
        if (epoch + 1) % (num_epochs // 10) == 0:
            print('episode losses at epoch {}:\n\tactor: {}\n\tcritic: {}'.format(
                epoch+1, avg_actor_loss, avg_critic_loss))
        train_on_memory()

    save_model(actor, 'actor')
    save_model(critic, 'critic')
    return actor, critic

if __name__ == '__main__':
    train(9, 4, num_epochs=100)
