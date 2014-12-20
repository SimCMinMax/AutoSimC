### Vars Init (we have to use an .ini file in the future and use a GUI maybe) ###
# You have to fill variables as it is on simcraft.
# If you want to optimize your gearset, specify only 1 item per slot and fill enchants on the section below.
# If you want to find BiS gearset, specify items that you want to compare in each slots.
c_profilename="Asteriksme"
c_profileid=0
c_class="monk"
c_race="human"
c_level="100"
c_spec="windwalker"
c_role="dps"
c_position="back"
c_talents="1133323"
c_glyphs="touch_of_death/fortuitous_spheres/floating_butterfly/spirit_roll/water_roll"

c_head="torias_perseverance,id=118894|cybergenetic_mechshades,id=109173,bonus_id=96/526/531"
c_neck="firecrystal_chain,id=118840,enchant=75mult|reavers_nose_ring,id=113851,enchant=40mult"
c_shoulders="studded_frostboar_leather_spaulders,id=118890|living_mountain_shoulderguards,id=113641,bonus_id=564/566,gems=35mult"
c_back="cloak_of_creeping_necrosis,id=113657,bonus_id=566,enchant=100mult|cloak_of_creeping_necrosis,id=113657,bonus_id=566,enchant=100mult"
c_chest="chestguard_of_the_roaring_crowd,id=113601,bonus_id=566|undying_chestguard,id=114498,bonus_id=57/560"
c_wrists="primal_gladiators_bindings_of_prowess,id=115675|primal_gladiators_armbands_of_prowess,id=115688"
c_hands="throatripper_gauntlets,id=113602,bonus_id=566|grips_of_vicious_mauling,id=113593,bonus_id=561/566"
c_waist="belt_of_bloody_guts,id=113636,bonus_id=566|belt_of_inebriated_sorrows,id=119338,bonus_id=566"
c_legs="supple_leggings,id=116178,bonus_id=189/526/536|leggings_of_broken_magic,id=113839,bonus_id=41/566"
c_feet="primal_gladiators_boots_of_cruelty,id=115671|face_kickers,id=113849"
c_finger1="primal_gladiators_ring_of_prowess,id=115771,enchant=50mult|flensers_hookring,id=113611,bonus_id=40/566,enchant=30mult"
c_finger2="timeless_solium_band_of_the_assassin,id=118297,enchant=50mult|timeless_solium_band_of_the_assassin,id=118297,enchant=30mult"
c_trinket1="lucky_doublesided_coin,id=118876|scales_of_doom,id=113612"
c_trinket2="skull_of_war,id=112318,bonus_id=526/530|lucky_doublesided_coin,id=118876"
c_main_hand="phemos_double_slasher,id=113667,bonus_id=564/566,gems=50mult,enchant=mark_of_the_shattered_hand|grandiose_longbow,id=115329,bonus_id=489/560,enchant=oglethorpes_missile_splitter"
c_off_hand="0"

# You have to add id of gems and enchants you want to compare, you can only compare 2 stats at a time.
c_en_gem_s1="gs1test"
c_en_gem_s2="gs2test"
c_en_ring_s1="rs1test"
c_en_ring_s2="rs2test"
c_en_neck_s1="ns1test"
c_en_neck_s2="ns2test"
c_en_back_s1="bs1test"
c_en_back_s2="bs2test"
c_en_main_hand="0" #If you add main_hand enchant(s), you must add off_hand enchant(s), they may be different
c_en_off_hand="0" #If you add off_hand enchant(s), you must add main_hand enchant(s), they may be different

### Enchant/Gems Arrays, DO NOT TOUCH ###
en_mh=["GS1","GS2","RS1","RS2","NS1","NS2","BS1","BS2"]
en_mh[0]=[15,14,15,13,14,12,13,11,12,10,11,9,10,8,9,7,8,6,7,5,6,4,5,3,4,2,3,1,2,0,1,0,1,1,2,0,1,1,0,0]
en_mh[1]=[0,1,0,2,1,3,2,4,3,5,4,6,5,7,6,8,7,9,8,10,9,11,10,12,11,13,12,14,13,15,14,15,14,14,13,15,14,14,15,15]
en_mh[2]=[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,0,1,1,0,0]
en_mh[3]=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,2,1,1,2,2]
en_mh[4]=[1,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]
en_mh[5]=[0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
en_mh[6]=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0]
en_mh[7]=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]

en_oh=["GS1","GS2","RS1","RS2","NS1","NS2","BS1","BS2"]
en_oh[0]=[16,15,16,14,15,13,14,12,13,11,12,10,11,9,10,8,9,7,8,6,7,5,6,4,5,3,4,2,3,1,2,0,1,1,2,0,1,1,0,0,1,0]
en_oh[1]=[0,1,0,2,1,3,2,4,3,5,4,6,5,7,6,8,7,9,8,10,9,11,10,12,11,13,12,14,13,15,14,16,15,15,14,16,15,15,16,16,15,16]
en_oh[2]=[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,0,1,1,0,0,1,0]
en_oh[3]=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,2,1,1,2,2,1,2]
en_oh[4]=[1,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0]
en_oh[5]=[0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1]
en_oh[6]=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,0,0]
en_oh[7]=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1]

### Split Vars to Lists ###
l_head=c_head.split('|')
l_neck=c_neck.split('|')
l_shoulders=c_shoulders.split('|')
l_back=c_back.split('|')
l_chest=c_chest.split('|')
l_wrists=c_wrists.split('|')
l_hands=c_hands.split('|')
l_waist=c_waist.split('|')
l_legs=c_legs.split('|')
l_feet=c_feet.split('|')
l_finger1=c_finger1.split('|')
l_finger2=c_finger2.split('|')
l_trinket1=c_trinket1.split('|')
l_trinket2=c_trinket2.split('|')
l_main_hand=c_main_hand.split('|')
l_off_hand=c_off_hand.split('|')

l_en_main_hand=c_en_main_hand.split('|')
l_en_off_hand=c_en_off_hand.split('|')

### Function wich print a simc profile ###
def scpout(oh):
    global c_profileid
    file.write(c_class+"="+c_profilename+"_"+str(c_profileid)+"\n")
    file.write("specialization="+c_spec+"\n")
    file.write("race="+c_race+"\n")
    file.write("level="+c_level+"\n")
    file.write("role="+c_role+"\n")
    file.write("position="+c_position+"\n")
    file.write("talents="+c_talents+"\n")
    file.write("glyphs="+c_glyphs+"\n")
    file.write("head="+c_head+"\n")
    file.write("neck="+c_neck+"\n")
    file.write("shoulders="+c_shoulders+"\n")
    file.write("back="+c_back+"\n")
    file.write("chest="+c_chest+"\n")
    file.write("wrists="+c_wrists+"\n")
    file.write("hands="+c_hands+"\n")
    file.write("waist="+c_waist+"\n")
    file.write("legs="+c_legs+"\n")
    file.write("feet="+c_feet+"\n")
    file.write("finger1="+c_finger1+"\n")
    file.write("finger2="+c_finger2+"\n")
    file.write("trinket1="+c_trinket1+"\n")
    file.write("trinket2="+c_trinket2+"\n")
    file.write("main_hand="+c_main_hand+"\n")
    if oh==1:
        file.write("off_hand="+c_off_hand+"\n\n")
    else:
        file.write("\n")
    c_profileid+=1
    return()

def scpopout(oh):
    global c_profileid
    file.write(c_class+"="+c_profilename+"_"+str(c_profileid)+"\n")
    file.write("specialization="+c_spec+"\n")
    file.write("race="+c_race+"\n")
    file.write("level="+c_level+"\n")
    file.write("role="+c_role+"\n")
    file.write("position="+c_position+"\n")
    file.write("talents="+c_talents+"\n")
    file.write("glyphs="+c_glyphs+"\n")
    file.write("head="+l_enchant[0]+"\n")
    file.write("neck="+l_enchant[1]+"\n")
    file.write("shoulders="+l_enchant[2]+"\n")
    file.write("back="+l_enchant[3]+"\n")
    file.write("chest="+l_enchant[4]+"\n")
    file.write("wrists="+l_enchant[5]+"\n")
    file.write("hands="+l_enchant[6]+"\n")
    file.write("waist="+l_enchant[7]+"\n")
    file.write("legs="+l_enchant[8]+"\n")
    file.write("feet="+l_enchant[9]+"\n")
    file.write("finger1="+l_enchant[10]+"\n")
    file.write("finger2="+l_enchant[11]+"\n")
    file.write("trinket1="+l_enchant[12]+"\n")
    file.write("trinket2="+l_enchant[13]+"\n")
    file.write("main_hand="+l_enchant[14]+"\n")
    if oh==1:
        file.write("off_hand="+l_enchant[15]+"\n\n")
    else:
        file.write("\n")
    c_profileid+=1
    return()

file=open('output.txt','w')
if len(l_head)+len(l_neck)+len(l_shoulders)+len(l_back)+len(l_chest)+len(l_wrists)+len(l_hands)+len(l_waist)+len(l_legs)+len(l_feet)+len(l_finger1)+len(l_finger2)+len(l_trinket1)+len(l_trinket2)+len(l_main_hand)+len(l_off_hand)!=16:
    for a in range(len(l_head)):
        c_head=l_head[a]
        for b in range (len(l_neck)):
            c_neck=l_neck[b]
            for c in range (len(l_shoulders)):
                c_shoulders=l_shoulders[c]
                for d in range (len(l_back)):
                    c_back=l_back[d]
                    for e in range (len(l_chest)):
                        c_chest=l_chest[e]
                        for f in range (len(l_wrists)):
                            c_wrists=l_wrists[f]
                            for g in range (len(l_hands)):
                                c_hands=l_hands[g]
                                for h in range (len(l_waist)):
                                    c_waist=l_waist[h]
                                    for i in range (len(l_legs)):
                                        c_legs=l_legs[i]
                                        for j in range (len(l_feet)):
                                            c_feet=l_feet[j]
                                            for k in range (len(l_finger1)):
                                                c_finger1=l_finger1[k]
                                                for l in range (len(l_finger2)):
                                                    c_finger2=l_finger2[l]
                                                    for m in range (len(l_trinket1)):
                                                        c_trinket1=l_trinket1[m]
                                                        for n in range (len(l_trinket2)):
                                                            c_trinket2=l_trinket2[n]
                                                            if c_off_hand!="0":
                                                                for o in range (len(l_main_hand)):
                                                                    c_main_hand=l_main_hand[o]
                                                                    for p in range (len(l_off_hand)):
                                                                        c_off_hand=l_off_hand[p]
                                                                        scpout(1)
                                                            else:
                                                                for o in range (len(l_main_hand)):
                                                                    c_main_hand=l_main_hand[o]
                                                                    scpout(0)
else:
    if c_off_hand!="0":
        for a in range(len(en_oh[0])):
            l_enchant=[c_head,c_neck,c_shoulders,c_back,c_chest,c_wrists,c_hands,c_waist,c_legs,c_feet,c_finger1,c_finger2,c_trinket1,c_trinket2,c_main_hand,c_off_hand]
            
            for b in range(en_oh[0][a]):
                l_enchant[b]=l_enchant[b]+",gem_id="+c_en_gem_s1
            for c in range(en_oh[1][a]):
                ca=en_oh[0][a]
                l_enchant[c+ca]=l_enchant[c+ca]+",gem_id="+c_en_gem_s2
            
            if en_oh[2][a]==2:
                l_enchant[10]=l_enchant[10]+",enchant_id="+c_en_ring_s1
                l_enchant[11]=l_enchant[11]+",enchant_id="+c_en_ring_s1
            elif en_oh[3][a]==2:
                l_enchant[10]=l_enchant[10]+",enchant_id="+c_en_ring_s2
                l_enchant[11]=l_enchant[11]+",enchant_id="+c_en_ring_s2
            else:
                l_enchant[10]=l_enchant[10]+",enchant_id="+c_en_ring_s1
                l_enchant[11]=l_enchant[11]+",enchant_id="+c_en_ring_s2
            
            if en_oh[4][a]==1:
                l_enchant[1]=l_enchant[1]+",enchant_id="+c_en_neck_s1
            elif en_oh[5][a]==1:
                l_enchant[1]=l_enchant[1]+",enchant_id="+c_en_neck_s2
            
            if en_oh[6][a]==1:
                l_enchant[3]=l_enchant[3]+",enchant_id="+c_en_back_s1
            elif en_oh[7][a]==1:
                l_enchant[3]=l_enchant[3]+",enchant_id="+c_en_back_s2
            
            if c_en_main_hand!="0":
                for d in range(len(l_en_main_hand)):
                    l_enchant[14]=l_enchant[14]+",enchant_id="+c_en_main_hand
                    for e in range(len(l_en_off_hand)):
                        l_enchant[15]=l_enchant[15]+",enchant_id="+c_en_off_hand
                        scpopout(1)
            else:
                scpopout(1)
    else:
        for a in range(len(en_mh[0])):
            l_enchant=[c_head,c_neck,c_shoulders,c_back,c_chest,c_wrists,c_hands,c_waist,c_legs,c_feet,c_finger1,c_finger2,c_trinket1,c_trinket2,c_main_hand]
            
            for b in range(en_mh[0][a]):
                l_enchant[b]=l_enchant[b]+",gem_id="+c_en_gem_s1
            for c in range(en_mh[1][a]):
                ca=en_mh[0][a]
                l_enchant[c+ca]=l_enchant[c+ca]+",gem_id="+c_en_gem_s2
            
            if en_mh[2][a]==2:
                l_enchant[10]=l_enchant[10]+",enchant_id="+c_en_ring_s1
                l_enchant[11]=l_enchant[11]+",enchant_id="+c_en_ring_s1
            elif en_mh[3][a]==2:
                l_enchant[10]=l_enchant[10]+",enchant_id="+c_en_ring_s2
                l_enchant[11]=l_enchant[11]+",enchant_id="+c_en_ring_s2
            else:
                l_enchant[10]=l_enchant[10]+",enchant_id="+c_en_ring_s1
                l_enchant[11]=l_enchant[11]+",enchant_id="+c_en_ring_s2
            
            if en_mh[4][a]==1:
                l_enchant[1]=l_enchant[1]+",enchant_id="+c_en_neck_s1
            elif en_mh[5][a]==1:
                l_enchant[1]=l_enchant[1]+",enchant_id="+c_en_neck_s2
            
            if en_mh[6][a]==1:
                l_enchant[3]=l_enchant[3]+",enchant_id="+c_en_back_s1
            elif en_mh[7][a]==1:
                l_enchant[3]=l_enchant[3]+",enchant_id="+c_en_back_s2
            
            if c_en_main_hand!="0":
                for d in range(len(l_en_main_hand)):
                    l_enchant[14]=l_enchant[14]+",enchant_id="+c_en_main_hand
                    scpopout(0)
            else:
                scpopout(0)
file.close
