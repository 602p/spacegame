from logging import debug, info, warn, error, critical
import pygame


UE_FIRE_ATTEMPT='UE_FIRE_ATTEMPT'						#ship, hardpoint				Called in ship context, immediatley when fire_item_in_hardpoint is called
UE_BEFORE_FIRE='UE_BEFORE_FIRE'							#item							Called in item context, immediatley before doing fire events
UE_AFTER_FIRE='UE_AFTER_FIRE'							#item							Called in item contest, immediatley after doing fire events
UE_FIRE_REQUIRE_FAIL='UE_FIRE_REQUIRE_FAIL'				#item							Called in item context, if checking fire_required fails
UE_FIRE_REQUIRE_SUCCESS='UE_FIRE_REQUIRE_SUCCESS'		#item							Called in item context, if checking fire_require succeedes
UE_FIRE_EQUIPPED='UE_FIRE_EQUIPPED'						#ship, hardpoint				Called in ship context, before attempting to call .fire() (in this case hardpoint is always filled)
UE_FIRE_UNEQUIPPED='UE_FIRE_UNEQUIPPED'					#ship, hardpoint 				Called in ship context, when the ship can't fire the hardpoint because nothing is equipped to it
UE_PROJECTILE_IMPACT='UE_PROJECTILE_IMPACT'				#projectile, hit 				Called in projectile context, when projectile hits something
UE_PROJECTILE_TIMEOUT='UE_PROJECTILE_TIMEOUT'			#projectile 					Called in projectile context, when projectile exceeds its lifetime
UE_STATE_CHANGE='UE_STATE_START'						#manager, oldstate, newstate	Called in statemgr context, when switching state

def sg_postevent(type_const, root, *a, **k):
	built_dict=k
	built_dict.update({
		"sg_type":type_const,
		"array_args":a,
		"dict_args":k,
		"root":root
	})
	pygame.event.post(pygame.event.Event(pygame.USEREVENT, built_dict))
	#debug("Posted an event of type "+type_const)
	#debug("-->"+str(built_dict))