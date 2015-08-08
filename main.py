from lib_enchant_table import *

### Reading settings.ini to init vars
import configparser
config = configparser.ConfigParser()
config.read('settings.ini')
profile = config['Profile']
gear = config['Gear']
enchant = config['Enchant']

c_profilename=profile['profilename']
c_profileid=int(profile['profileid'])
c_class=profile['class']
c_race=profile['race']
c_level=profile['level']
c_spec=profile['spec']
c_role=profile['role']
c_position=profile['position']
c_talents=profile['talents']
c_glyphs=profile['glyphs']

c_other=profile['other']

c_head=gear['head']
c_neck=gear['neck']
if config.has_option('Gear', 'shoulders'): c_shoulders=gear['shoulders']
else: c_shoulders=gear['shoulder']
c_back=gear['back']
c_chest=gear['chest']
if config.has_option('Gear', 'wrists'): c_wrists=gear['wrists']
else: c_wrists=gear['wrist']
c_hands=gear['hands']
c_waist=gear['waist']
c_legs=gear['legs']
c_feet=gear['feet']
c_finger1=gear['finger1']
c_finger2=gear['finger2']
c_trinket1=gear['trinket1']
c_trinket2=gear['trinket2']
c_main_hand=gear['main_hand']
if config.has_option('Gear', 'off_hand'): c_off_hand=gear['off_hand']
else: c_off_hand=""

c_en_gem_s1=enchant['gem_stat1']
c_en_gem_s2=enchant['gem_stat2']
c_en_ring_s1=enchant['ring_stat1']
c_en_ring_s2=enchant['ring_stat2']
c_en_neck_s1=enchant['neck_stat1']
c_en_neck_s2=enchant['neck_stat2']
c_en_back_s1=enchant['back_stat1']
c_en_back_s2=enchant['back_stat2']
c_en_main_hand=enchant['main_hand']
c_en_off_hand=enchant['off_hand']

### Split vars to lists ###
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
    global c_profileid, c_other
    file.write(c_class+"="+c_profilename+"_"+str(c_profileid)+"\n")
    file.write("specialization="+c_spec+"\n")
    file.write("race="+c_race+"\n")
    file.write("level="+c_level+"\n")
    file.write("role="+c_role+"\n")
    file.write("position="+c_position+"\n")
    file.write("talents="+c_talents+"\n")
    file.write("glyphs="+c_glyphs+"\n")
    if c_other!="": file.write(c_other+"\n")
    file.write("head="+l_gear[0]+"\n")
    file.write("neck="+l_gear[1]+"\n")
    file.write("shoulders="+l_gear[2]+"\n")
    file.write("back="+l_gear[3]+"\n")
    file.write("chest="+l_gear[4]+"\n")
    file.write("wrists="+l_gear[5]+"\n")
    file.write("hands="+l_gear[6]+"\n")
    file.write("waist="+l_gear[7]+"\n")
    file.write("legs="+l_gear[8]+"\n")
    file.write("feet="+l_gear[9]+"\n")
    file.write("finger1="+l_gear[10]+"\n")
    file.write("finger2="+l_gear[11]+"\n")
    file.write("trinket1="+l_gear[12]+"\n")
    file.write("trinket2="+l_gear[13]+"\n")
    file.write("main_hand="+l_gear[14]+"\n")
    if oh==1:
        file.write("off_hand="+l_gear[15]+"\n\n")
    else:
        file.write("\n")
    c_profileid+=1
    return()

file=open('out.simc','w')
if len(l_head)+len(l_neck)+len(l_shoulders)+len(l_back)+len(l_chest)+len(l_wrists)+len(l_hands)+len(l_waist)+len(l_legs)+len(l_feet)+len(l_finger1)+len(l_finger2)+len(l_trinket1)+len(l_trinket2)+len(l_main_hand)+len(l_off_hand)!=16:
    l_gear=["head","neck","shoulders","back","chest","wrists","hands","waist","legs","feet","finger1","finger2","trinket1","trinket2","main_hand","off_hand"]
    for a in range(len(l_head)):
        l_gear[0]=l_head[a]
        for b in range (len(l_neck)):
            l_gear[1]=l_neck[b]
            for c in range (len(l_shoulders)):
                l_gear[2]=l_shoulders[c]
                for d in range (len(l_back)):
                    l_gear[3]=l_back[d]
                    for e in range (len(l_chest)):
                        l_gear[4]=l_chest[e]
                        for f in range (len(l_wrists)):
                            l_gear[5]=l_wrists[f]
                            for g in range (len(l_hands)):
                                l_gear[6]=l_hands[g]
                                for h in range (len(l_waist)):
                                    l_gear[7]=l_waist[h]
                                    for i in range (len(l_legs)):
                                        l_gear[8]=l_legs[i]
                                        for j in range (len(l_feet)):
                                            l_gear[9]=l_feet[j]
                                            for k in range (len(l_finger1)):
                                                l_gear[10]=l_finger1[k]
                                                for l in range (len(l_finger2)):
                                                    l_gear[11]=l_finger2[l]
                                                    for m in range (len(l_trinket1)):
                                                        l_gear[12]=l_trinket1[m]
                                                        for n in range (len(l_trinket2)):
                                                            l_gear[13]=l_trinket2[n]
                                                            if c_off_hand!="":
                                                                for o in range (len(l_main_hand)):
                                                                    l_gear[14]=l_main_hand[o]
                                                                    for p in range (len(l_off_hand)):
                                                                        l_gear[15]=l_off_hand[p]
                                                                        scpout(1)
                                                            else:
                                                                for o in range (len(l_main_hand)):
                                                                    l_gear[14]=l_main_hand[o]
                                                                    scpout(0)
else:
    if c_off_hand!="":
        for a in range(len(en_oh[0])):
            l_gear=[c_head,c_neck,c_shoulders,c_back,c_chest,c_wrists,c_hands,c_waist,c_legs,c_feet,c_finger1,c_finger2,c_trinket1,c_trinket2,c_main_hand,c_off_hand]
            
            for b in range(en_oh[0][a]):
                l_gear[b]=l_gear[b]+",gem_id="+c_en_gem_s1
            for c in range(en_oh[1][a]):
                ca=en_oh[0][a]
                l_gear[c+ca]=l_gear[c+ca]+",gem_id="+c_en_gem_s2
            
            if en_oh[2][a]==2:
                l_gear[10]=l_gear[10]+",enchant_id="+c_en_ring_s1
                l_gear[11]=l_gear[11]+",enchant_id="+c_en_ring_s1
            elif en_oh[3][a]==2:
                l_gear[10]=l_gear[10]+",enchant_id="+c_en_ring_s2
                l_gear[11]=l_gear[11]+",enchant_id="+c_en_ring_s2
            else:
                l_gear[10]=l_gear[10]+",enchant_id="+c_en_ring_s1
                l_gear[11]=l_gear[11]+",enchant_id="+c_en_ring_s2
            
            if en_oh[4][a]==1:
                l_gear[1]=l_gear[1]+",enchant_id="+c_en_neck_s1
            elif en_oh[5][a]==1:
                l_gear[1]=l_gear[1]+",enchant_id="+c_en_neck_s2
            
            if en_oh[6][a]==1:
                l_gear[3]=l_gear[3]+",enchant_id="+c_en_back_s1
            elif en_oh[7][a]==1:
                l_gear[3]=l_gear[3]+",enchant_id="+c_en_back_s2
            
            if c_en_main_hand!="":
                for d in range(len(l_en_main_hand)):
                    l_gear[14]=c_main_hand
                    l_gear[14]=l_gear[14]+",enchant_id="+l_en_main_hand[d]
                    for e in range(len(l_en_off_hand)):
                        l_gear[15]=c_off_hand
                        l_gear[15]=l_gear[15]+",enchant_id="+l_en_off_hand[e]
                        scpout(1)
            else:
                scpout(1)
    else:
        for a in range(len(en_mh[0])):
            l_gear=[c_head,c_neck,c_shoulders,c_back,c_chest,c_wrists,c_hands,c_waist,c_legs,c_feet,c_finger1,c_finger2,c_trinket1,c_trinket2,c_main_hand]
            
            #for b in range(en_mh[0][a]):
                #l_gear[b]=l_gear[b]+",gem_id="+c_en_gem_s1
            #for c in range(en_mh[1][a]):
                #ca=en_mh[0][a]
                #l_gear[c+ca]=l_gear[c+ca]+",gem_id="+c_en_gem_s2
            
            if en_mh[2][a]==2:
                l_gear[10]=l_gear[10]+",enchant_id="+c_en_ring_s1
                l_gear[11]=l_gear[11]+",enchant_id="+c_en_ring_s1
            elif en_mh[3][a]==2:
                l_gear[10]=l_gear[10]+",enchant_id="+c_en_ring_s2
                l_gear[11]=l_gear[11]+",enchant_id="+c_en_ring_s2
            else:
                l_gear[10]=l_gear[10]+",enchant_id="+c_en_ring_s1
                l_gear[11]=l_gear[11]+",enchant_id="+c_en_ring_s2
            
            if en_mh[4][a]==1:
                l_gear[1]=l_gear[1]+",enchant_id="+c_en_neck_s1
            elif en_mh[5][a]==1:
                l_gear[1]=l_gear[1]+",enchant_id="+c_en_neck_s2
            
            if en_mh[6][a]==1:
                l_gear[3]=l_gear[3]+",enchant_id="+c_en_back_s1
            elif en_mh[7][a]==1:
                l_gear[3]=l_gear[3]+",enchant_id="+c_en_back_s2
            
            if c_en_main_hand!="":
                for d in range(len(l_en_main_hand)):
                    l_gear[14]=c_main_hand
                    l_gear[14]=l_gear[14]+",enchant_id="+l_en_main_hand[d]
                    scpout(0)
            else:
                scpout(0)
file.close
