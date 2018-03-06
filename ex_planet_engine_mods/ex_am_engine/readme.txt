1. I moved the terraforming events into a scripted effect. This effect is fired directly from the terraforming links upon terraforming completion. 
This effect can also be enabled to fire on non-vanilla planets using the synergy triggers, and you can of course do any effect you want. 

2. I've set up a unique global flag for your mod for this engine to run. I've intentionally placed it as a game start flag + a contingency, to make 
sure that other mods that run on game start can find it (the event name is fine tuned respective of the other mods).

3. you can rename every file I made, but make sure that the scripted triggers/effects retain their load order in the naming.

4. I added a bunch of graphical stuff and entities - these are required to not generate errors.

5. Habitability Traits, Planet Localisations, and the planet classes file are shared by all mods. If you want to make changes to these, the other mods need to be updated with the changes as well - to avoid problems. 

6. look under scripted_triggers to see the synergy triggers file - you can use them as you see fit to make sure your mod synergies with 'em planet mods.