from logging import debug, info, warn, error, critical
import pygame

	
UE_FIRE_ATTEMPT='UE_FIRE_ATTEMPT'				  #ship, hardpoint						Called in ship context, immediatley when fire_item_in_hardpoint is called
UE_FIRE_EQUIPPED='UE_FIRE_EQUIPPED'				  #ship, hardpoint						Called in ship context, before attempting to call .fire() (in this case hardpoint is always filled)
UE_FIRE_UNEQUIPPED='UE_FIRE_UNEQUIPPED'			  #ship, hardpoint 						Called in ship context, when the ship can't fire the hardpoint because nothing is equipped to it

UE_BEFORE_FIRE='UE_BEFORE_FIRE'					  #item									Called in item context, immediatley before doing fire events
UE_AFTER_FIRE='UE_AFTER_FIRE'					  #item									Called in item contest, immediatley after doing fire events
UE_FIRE_REQUIRE_FAIL='UE_FIRE_REQUIRE_FAIL'		  #item									Called in item context, if checking fire_required fails
UE_FIRE_REQUIRE_SUCCESS='UE_FIRE_REQUIRE_SUCCESS' #item									Called in item context, if checking fire_require succeedes

UE_PROJECTILE_IMPACT='UE_PROJECTILE_IMPACT'		  #projectile, hit 						Called in projectile context, when projectile hits something
UE_PROJECTILE_TIMEOUT='UE_PROJECTILE_TIMEOUT'	  #projectile 							Called in projectile context, when projectile exceeds its lifetime

UE_STATE_CHANGE='UE_STATE_START'				  #manager, oldstate, newstate			Called in statemgr context, when switching state

UE_SYSTEM_REPAIRED='UE_SYSTEM_REPAIRED'			  #manager, system 						Called in damagesystem when system is repaired
UE_SYSTEM_DAMAGED='UE_SYSTEM_DAMAGED'			  #manager, system 						Called in damagesystem when system is damaged
UE_SYSTEM_DESTROYED='UE_SYSTEM_DESTROYED'		  #manager, system 						Called in damagesystem when system is destroyed

UE_DAMAGE_DEALT='UE_DAMAGE_DEALT'				  #system, amount, peirce, source, x, y	Called in damagemodel when damag is dealt
UE_SHL_DAMAGE_DEALT='UE_SHL_DAMAGE_DEALT'		  #system, amount, source, x, y			Called in damagemodel when shield damag is dealt
UE_HUL_DAMAGE_DEALT='UE_HUL_DAMAGE_DEALT'		  #system, amount, source, x, y			Called in damagemodel when hull damag is dealt
UE_SHIELDS_DOWN='UE_SHIELDS_DOWN'				  #system, source, x, y					Called in damagemodel when shields fail
UE_SHIP_DESTROYED='UE_SHIP_DESTROYED'			  #system, source						Called in damagemodel when ship explodes

UE_SHIP_DIE_RUN='UE_SHIP_DIE_RUN'				  # ship 								Called in ship when ship.die() is run


def sg_postevent(type_const, *a, **k):
	built_dict=k
	built_dict.update({
		"sg_type":type_const,
		"array_args":a,
		"dict_args":k
	})
	pygame.event.post(pygame.event.Event(pygame.USEREVENT, built_dict))
	#debug("Posted an event of type "+type_const)
	#debug("-->"+str(built_dict))