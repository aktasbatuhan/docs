Title: Designing DePIN Protocols Using Optimal Control Theory

URL Source: https://volt.capital/blog/designing-depin-protocols-using-optimal-control-theory

Markdown Content:
[writing](https://volt.capital/writing)

/

Designing DePIN Protocols Using Optimal Control Theory

Assessing crypto protocols – or quantitatively measuring them against some desiderata – seems like a simple task, but it quickly becomes complex. You can collect data, model the protocol mathematically, analyze revenues, or perform advanced Token Go Up analysis. How do these methods, however, translate to actual design decisions founders can implement?

‍

Our recent focus on DePIN is motivated by laying the groundwork for these smart design decisions by evaluating the current paradigms and proposing better ones when appropriate. One of these paradigms is Burn-and-Mint Equilibrium (BME), a widespread inflation control rule introduced by Factom and popularized by Helium. While effective at controlling highly inflationary node rewards, our interest is in _how_ effective it is, especially when compared to theoretical limits or other designs. To do this, we’ll reach towards the field of _optimal control theory_ and assess BME as a one possible controller in generalized DePIN systems.

‍

The primary goal of this post is to lay a framework to answer some important questions: how well will my protocol design choice perform? How well _can_ it perform, and what’s the gap between the best-case and my implementation? By asking and answering these questions for BME and inflation controllers, we hope to exhibit a repeatable and generalizable process that designers can use for other important problems.

‍

Preliminaries
-------------

### Defining BME

BME is a simple scheme of dynamically adjusting the circulating supply of a token. Although its actual implementation may differ from protocol to protocol, the core flow is as follows:

‍

1.   Users looking to pay for the network’s services, say $100 worth, must buy the equivalent amount of the protocol token. If the token is worth $2, they purchase 50 tokens. In modern protocols, this process is abstracted away by allowing users to pay $100 in stablecoins, which the protocol converts into tokens while storing the stablecoin in reserves.
2.   The protocol then _burns_ these tokens while retaining the equivalent paid value in stablecoin reserves.
3.   The network emits a set target amount of tokens per month (or any other cadence) as rewards to service providers.

‍

The goal of this is to introduce a dynamic equilibrium between the price of the token and the circulating supply. Consider two cases in which $100 of service is purchased. If the token is very expensive, then a smaller amount of tokens will be burned, causing net surplus inflation. If the token is cheap, then a larger amount will be burned, resulting in net deflation. As this continues over several timesteps, the system will _theoretically_ correct the price of the token until the burned and minted amounts are equal.

‍

### Why are Inflation Controllers Necessary?

A natural first step in analyzing BME is retracing the first-principles that led to its development. Why do DePINs need BME while other crypto protocols can adopt simpler fixed inflation or maximum supply schemes?

‍

Unlike other protocols, geographical location, service capacity, and reliable uptime of each DePIN provider are crucial to the value of the network. A Helium provider provisioning several nodes in Manhattan is just as important as a small provider in rural Idaho, yet the latter would be economically unviable without ample subsidy. Network designers generally _want_ as much expansion and coverage as possible, so regularly inflating the supply to subsidize these providers is a necessary design choice.

‍

In a naive model, user demand tokens are distributed to the providers that served them, similar to a peer-to-peer direct exchange. Our model, recognizing the need to subsidize smaller providers, must procure tokens from _somewhere else_ to pay subsidies. The only way to do this is consistent network inflation.

‍

As a result of our inflationary model, however,the network economics become highly unsustainable. Designers clearly need some sort of mechanism to counteract the inflation of tokens, and BME has been the standard mechanism to accomplish this since Helium’s implementation.

‍

### Optimal Control Theory

As mentioned above, our goal is to quantify the optimality of BME and theoretical inflation controllers in general. To achieve this, we use the field of _Optimal Control_. Control theory, more broadly, studies _controllers_, or mechanisms that augment the inputs of a system with the goal of steering the system towards an ‘ideal’ state. Everyday products like air conditioning rely on controllers to regulate the system towards a set temperature. For most applications of control theory, these systems are modeled as _dynamical systems_, where the system behavior is governed by a set of differential equations. The foundation for modeling crypto protocols as dynamical systems is laid out in the work of [Michael Zargham](https://arxiv.org/pdf/1807.00955) and others. We also draw from the theory in [this paper](https://arxiv.org/pdf/2210.12881) due to Ackin et. al. Using this framework, we can skip the low-level math needed to construct a coherent model and begin describing our system directly.

‍

More formally, we can define a state vector and a control vector . The state vector will define the time-variant snapshot of the DePIN economy:token supply, price, the number of users on the network, etc. The control vector will encode the actions of our inflation controller (i.e. BME or some theoretical controller). We’ll also have some exogenous inputs like demand or macro sentiment, which we’ll represent as a vector .

‍

Overall, the dynamics of our system will be given by

Where the function is just a representation of a state-transition operator. With this framing, we can start optimizing the control vector by minimizing cost , which we’ll define and work with later.

‍

DePIN as a Dynamical System
---------------------------

The first step in our analysis is to create a well-defined model of a general DePIN economy. There are _several_ approaches to doing this in the literature, but one important and relevant approach is the _dynamical system_. A simple definition of dynamical systems is a set of rules (equations) that describe how a system evolves over time. To better understand the power and limitations of this approach, however, we’ll need to dig a little deeper.

‍

Any large, complex system is made of evolving components, each affecting the other components. Modeling the entirety of this system by capturing the comprehensive nuances of its components is not feasible and, more importantly, not very useful. What _is_ useful about this approach is the ability to center some part of the system as our interest of study. In the classical example of modeling an ecosystem of predator and prey, there are innumerable variables that could be modeled to exact precision. For example, how does the number of predators affect the number of prey? To _really_ answer this, we need to know how much vegetation the environment produces – more edible plants means less need for hunting prey. We’ll have to model the sunlight, water, soil, ideal growth conditions, etc.

‍

Each new question opens entirely new subsystems to be modeled, and the point of our modeling is lost by attempting to flesh them out. Instead, we can observe that these subsystems produce some measurable result or pattern and black box the details of the system. Our food supply question can be reduced to “roughly how much vegetation grows over some time period?”. The subsystem of food growth will not be modeled rigorously, and we can roughly estimate its output to answer the question of interest: what are the dynamics of predator and prey populations?

‍

Using these same principles, our dynamical systems model of DePIN protocols is motivated by the specific subsystem that we are looking to study and improve: token supply control. Other processes like macro sentiment, provider and user inflows, and usage rates should be given modeling rigor based on their influence on token supply control. We’ll begin by defining which variables we’re interested in tracking.

‍

### Model Set-Up

With the table set, we can build our model of a general DePIN economy as a dynamical system. As mentioned in the preliminaries, we’ll need to define a state vector. Our state vector will consist of the variables that describe the relevant values that evolve over time:

‍

We’ll also have to model some exogenous inputs that are crucial to the dynamics of our system, namely the demand for services and the token in general, along with a ‘market factor’ to approximate the conditions of the market. We’ll call this exogenous set of inputs .

Although this may seem like a lot, our driving principle is simplicity – we _only_ include those variables that would render the model useless if left out. The reality is that DePIN economies are complex, and ignoring too much of that complexity will dilute the usefulness of our results.

‍

We’ll also define a control vector , which will contain variables we can change with our inflation controller policy:

‍

How do we encode an inflation rule, or _policy_, into the model? As our end goal is to find the best performing policy, we’ll need some way to represent inflation policies in general, not just BME. Denoting inflation policies as , we simply define functions for how and are calculated. For BME:

‍

The BME policy is simple. We’ll burn the equivalent USD income value of tokens and emit some fixed amount of tokens .

‍

Now that our state variables and exogenous inputs are set, we can relate them in our _system dynamics_. This is the actual description of how these states influence each other when evolving over time. We’ll have one equation for each state variable:

‍

‍

The above model lays out the core flow of the most important variables. To describe each:

*   Supply evolves with burning and minting, and the USD value used to purchase tokens is added to reserves.
*   Price is calculated as a ‘fundamental’ price which measures the ratio of demand and supply with some adjustments for utilization and macro effects.
*   Capacity grows with the price of the token under the assumption that providers are enticed to join.
*   Utilization, or how much of capacity is being used, is a ratio of service demand and capacity.

‍

While there are other elements of this model that are necessary to perform the analysis below, like sensitivity parameters for different inputs, they are less important to developing an intuitive understanding, which is the primary goal of this post. With our system dynamics set, we have developed enough rigor to begin some interesting and powerful analysis.

‍

Optimize, Optimize, Optimize
----------------------------

To begin optimizing our inflation controller, we need a way to measure how ‘good’ any given controller actually is. What are we optimizing for? There’s no correct answer to this question – protocol designers may have wildly different goals for different use cases. Certain token structures may require minimally volatile token prices while others may look for a more delicate balance between user demand and service capacity.

‍

### Defining an Optimal Inflation Policy

For our use case, we’ll aim to create a well-rounded set of desired outcomes to test our controllers against in a simulation:

‍

1.   Stable, moderate price growth
2.   Service capacity grows steadily.
3.   Service utilization stays above 75%.

‍

Each of these outcomes will have adjustable weights in our _stage cost_ , which will penalize deviations from this ideal state at each timestep. Over some amount of time, we can aggregate each step’s stage cost to get our _cost function_ :

‍

‍

While the notation may seem daunting, the actual meaning of this function is not complicated. We’ll add up the stage costs at each timestep and take the expected value of that sum to account for the randomness in our simulation. This short function, which has the rest of our model baked in, gives us a number for how good the control policy was at pulling our system towards the ideal state. We can plug in or some other policy and compare their performance directly – higher values indicate worse performance. The interesting question, however, is which choice of  results in the _lowest possible_ value of ? This can be represented as , or the _optimal_ control policy:

‍

‍

### Solving for

While our problem may seem simple, solving for this function in a complex, high-dimensional simulation is not feasible to do by hand. Instead, we’ll borrow from machine learning and dynamic programming to approximate . The full details of this process are outside the scope of this post (and in the scope of the eventual paper!), but we’ll outline the approach here.

‍

1.   **Value Function.**We reframe this problem in a reinforcement learning lens, where agents in a state space make decisions and quantify how ‘good’ those decisions are. Robots, for example, can be trained to navigate some space and calculate the ‘goodness’ of their actions based on a cost function like ours. In our model, the inflation controller is the agent operating in a high-dimensional state space. Agents make decisions based on ‘value functions’, which give the cost of doing some action in a given state. Similarly, the inflation controller makes decisions based on _all_ of the variables and how the decision drives the system towards the ideal state.
2.   **Function Approximation.**We approximate this value function using [_value iteration_ and the Bellman equation](https://medium.com/@ngao7/markov-decision-process-value-iteration-2d161d50a6ff). In essence, this process involves ‘training’ a large function that maps different states to actions.
3.   **Optimal Control.**With our approximated value function, we can use BFGS minimization to find the control values (our vector ) that minimize the current cost and expected future costs.

‍

This process enables our simulation to find the approximate optimal control action at every timestep, which we can compare as a baseline against BME and other types of controllers. While inflation policies in practice are often simple heuristic rules, our optimal controller will make dynamic decisions. An important caveat here is that our 5-dimensional state space requires that we use approximation, as deriving a closed form of the value function and getting exact optimal values is not feasible. As a result, our optimal actions are not exact.

‍

Testing Controllers
-------------------

This setup allows us to test design ideas against a baseline as desired or run experiments on different design approaches. One such experiment asks the following question: while BME burns 100% of tokens, what would happen if we burned a portion instead? The intuitive expectation is that deflationary effects of burning would be dampened, supply would go up, and price of the token should go down. The nuances that our simulations will explain, however, include the connection between demand, service purchased, token price, capacity, and other exogenous factors.

‍

Using a similar simulation framework and set of parameters as our [DePIN Simulation Widget](https://depin-sim.streamlit.app/), we model the performance of our optimal controller, BME, and two modified versions of BME that burn 75% and 50% of the tokens paid for service. We ran this simulation 50 times with some randomness from different stochastic inputs.

‍

![Image 1](https://cdn.prod.website-files.com/628cfc99b32e9128c13d1f3a/68279a9443978e374a5d634a_AD_4nXcLCG5Is-uDExOpki5T9kHpjX_Z-jLb9nEb_qsEiIyCBe10kr0Ffon-9LM4L75wy0luImTXE7WUMCAyWdXcfVeTpSFyGkaQ1-VF0HPr7SfX9TwCyIj9qSLEB5Km_R1x3SXviqqx4Q.png)

‍

Step cost measures how much a controller deviated from our optimal trajectory. As expected, our optimal controller had the lowest step cost, while BME had the highest. Interestingly enough, lower percentage burned resulted in lower step cost, which _should_ imply that our optimal controller had the lowest percentage of token income burned.

‍

![Image 2](https://cdn.prod.website-files.com/628cfc99b32e9128c13d1f3a/68279a93afddd5d6d9ca06a5_AD_4nXcr0MeAVCM2LrtlZgBMcXRb9AjpkFrwzm4GGygy9mqAFTDSTjCM2wlMsUA88CsNtHYISuN7zwE2B1zFJAkiQfMCaTHe0IrdXpFqAT-Q8P_BCfmJyjnv38gZPXTEokMQPSCKRHBnDQ.png)

Surprisingly, our optimal policy actually burns the _second most_ of any policy. The downward slope in the other policies is due to the stochastic result of our demand data, which happened to be lower in this sample. Even with this, the amount of tokens burned remained steady in our optimal policy, even with incomes seemingly going down. Let’s take a look at the distribution of burn and mint actions for each policy:

‍

![Image 3](https://cdn.prod.website-files.com/628cfc99b32e9128c13d1f3a/68279a93909023fde82bb45b_AD_4nXfZYkw0Hac13zpwNbrUzVHLJuBGG3gL37T3SrKpWwkataPpMVlvOLG1I8ly4wZXAJbAxmtkoi1WXBrsbz3EnxSd5Uu-K-FY8d2mCwX0dbPB69eHsqeqRgFcjtRdlHS09vl-topq8A.png)

![Image 4](https://cdn.prod.website-files.com/628cfc99b32e9128c13d1f3a/68279a948e3bb701705d0174_AD_4nXdl_sfcYOjHFLCvYCPyb22FRMEmir1NHKPPNnT-A_HdOdF2J9yUhNqlmMEXf8d5TNHKD_LJmh2LtnRzmge1OQN6B4_H3uglMKHr8YyCm-sLBNH2SEvVq8yHEgwvx1I2lANjGH_S.png)

‍

As BME and its variant policies all have target emission rates, they strictly minted 20,000 tokens per timestep This parameter was fine-tuned when balancing the simulation. The optimal policy, however, never exceeded _half_ of that. Additionally, the optimal policy burned a wide range of values, staying somewhat in line with BME’s general range. Its emissions also span a much larger range.

‍

How did our policies do for token price?

‍

![Image 5](https://cdn.prod.website-files.com/628cfc99b32e9128c13d1f3a/68279a94d2b66db031605415_AD_4nXftvZ1GUFQ_l_8dc6KLfTQsQZqg9uoswvcQtsdo6qWG7Nx3lHaGbgQ7VoMtQ6YvHjjPt-36wXh2yUnB2ZABElFfZMCjw-m_AR0rSpV76imJbl2l-8Y6Vy8vI0DOQW_QVtt6yqV6Dg.png)

‍

It should be noted that price here is calculated as a simple ratio of token demand and token supply with some exogenous macro adjustment. Not too surprisingly, the BME variant price performance is in order of the percent of tokens burned. Our optimal policy, however, has a steadily increasing price. Although BME burned the most tokens, it also overemitted at each timestep, as did the 50% and 75% variants.

‍

This can be seen clearly in the final circulating supplies for each policy:

‍

![Image 6](https://cdn.prod.website-files.com/628cfc99b32e9128c13d1f3a/68279a947c09f9fd8bc4e9ac_AD_4nXediQX9MCS0_Qzxi-ooQfSdCfh7blfwnFEmX8LXL2RwB3ksm1PcaepITl5VP_zsbJI-gyuLxiMZJ0WyWjs1PF4bC454sHfAyMDq3JgqDipOhZeoAoIlA-cJOgc2WlTcjJHaThBKFg.png)

‍

This implies that inflation control policies that aim for ‘target’ emissions lack any dynamic response to the complex web of interactions in DePIN economies. When other parts of the system experience exogenous shocks or markets are bearish, the environments become even _more_ inflationary as demand drops.

‍

In practice, however, implementing volatile and fully dynamic minting is not feasible in DePIN economies. Providers need steady streams of income, and sudden changes in rewards will only drive prospective providers away. A natural first approach to addressing this is to find some sort of middle ground. Can we introduce dynamic emission while maintaining some stability and predictability? On a weekly basis, for example, the protocol can adjust minting targets based on a projection of the previous week’s income. The logic here is simple: service income is directly tied to the amount of tokens burned, and our policy will look to inflate the supply by an equal amount. After adapting this to our simulation, we can plug it into the policy comparison, labeled as “Dynamic” below:

‍

‍

![Image 7](https://cdn.prod.website-files.com/628cfc99b32e9128c13d1f3a/68279a942b80c4e38059716f_AD_4nXfSVfHft007t2oB8w9pULAUNjD45-Og3r1jNRAhnxwnRaezCTU-qDkcg-ZLrgwur1yAeR-pfAXSVcVWOkbBeNrW4yDkg13PfUn_HZD68ee1Th7OB7pOCLm8MVg7LW8n3hqIYSX-aQ.png)

![Image 8](https://cdn.prod.website-files.com/628cfc99b32e9128c13d1f3a/68279a94f04507785aabe60c_AD_4nXdtbhqtLTwDu0SVOqRNJQ5Wb3wM7GWW6-Bp9TDp-ZQ5WjLAcGcgNYrY4A2fCSVmV6_rEnu9hw0LJZMjYqUCu_8XQl1VeHlu8Jee0ATzVAgkgf1B1ohvhJYgNVRkcFL7kY444wAdDw.png)

![Image 9](https://cdn.prod.website-files.com/628cfc99b32e9128c13d1f3a/68279a94236c440fddbe64a3_AD_4nXe1kGiVEuFNIqhSY-sLLkBAf53UWaj5-8ecNnakdTj-D0OvQj65Ai2kN7bn3mnMieJ_LaSlyDjOlq7TkOpnRkJH0r2SHUs8kEbC54CE7Ak3Stm_Wi1TTL5h7k-5sDGggdteL7LbgA.png)

‍

Our new policy has much better price performance while maintaining relatively stable rewards, even when adapting a new emission rate every 5 timesteps. Price becomes more stable and grows, which indicates a slightly deflationary environment. The policy, given stable enough income, will not shoot emissions up and down enough to degrade the provider experience. In practice, however, DePINs may have large swings in usage. This policy can be capped by some maximum percentage change to avoid unpredictable swings.

‍

This is just one way to improve upon our inflation policy. As we iterate, we can test and tweak our parameters, test different exogenous environments, and try to find the most resilient solution for the volatile and unpredictable real world implementation.

‍

Using This Model and Future Work
--------------------------------

‍

This method of analysis, while somewhat computationally involved, is not difficult to implement for any protocol designer looking to optimize a part of their design. The true value of this approach is a reliable baseline to compare protocol decisions against. Although simulations can provide some idea of how ‘well’ a protocol design choice can play out under the right conditions, it’s more helpful to establish a lower bound and search the design space for the most optimal feasible version. In our case, we’ve found that BME and the optimal case have a large enough gap to warrant further study, and we proposed a simple mechanism that seems to have better performance overall.

‍

The foundation that we laid here is a starting point for more impactful analysis when customized for a specific protocol. After plugging in their desiderata and finding optimal bounds, protocol designers can analyze patterns in different macro conditions, demand profiles, user adoption scenarios, etc. to battle-test their ideas.

‍

Looking ahead, our work continues towards introducing a game-theoretic aspect to this model, in which we show that proposed designs are not attackable by users or providers. We’ll explore other elements of DePIN economies for this form of analysis in the pursuit of a generalized framework.

‍

