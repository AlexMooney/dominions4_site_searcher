##########################
# Configuration parameters

SITEFREQ = 0.45  # chance of a slot to be occupied
TERRAIN = 1  # this is a bitmask I can deal with later; 1 is plains
UNFOUNDSITES = 8  # we've found 1, for example
PRIORSEARCH = [4, 0, 0, 0, 0, 0, 0, 0, 0]
SCHOOLS = ['Fire', 'Air', 'Water', 'Earth',
           'Astral', 'Death', 'Nature', 'Blood', 'Holy']
RARITY = [60, 9, 1]  # normalize site by rarity to get empirical probabilities


###################
# Read in site data
#
# siteData format. Note empty strings instead of '0's (whitespace not in file)
# 0,  1,       2,     3,  4,    5,   6,7,8,9,10,11,12,13,14
# id, name,    rarity,loc,level,path,F,A,W,E,S, D, N, B, gold
# 210,Tar Pits,0,     219,1,    Fire,1, , , , ,  ,  ,  ,
#
# full list of sites allowed by terrain
# example using Tar Pits, above
# site = { 'school':0, 'rarity':60, 'level':1, 'schoolGems':1, 'otherGems':0 }

allSites = []
unknownSites = []
for sline in [line.split(',') for line in open('test_siteData.csv', 'r')]:
    if (int(sline[3]) & TERRAIN) and (sline[4] != '0'):
        site = {'school': SCHOOLS.index(sline[5]),
                'rarity': RARITY[int(sline[2])],
                'level': int(sline[4]),
                }
        try:
            site['schoolGems'] = int(sline[6+site['school']])
            if site['school'] == 8:
                site['schoolGems'] = 0  # otherwise, gold becomes holy gems!
        except ValueError:
            site['schoolGems'] = 0
        site['otherGems'] = sum([int(g if g != '' else 0)
                                 for g in sline[6:14]])
        site['otherGems'] -= site['schoolGems']
        if site['otherGems'] < 0:
            print(site)
        allSites.append(site)
        if PRIORSEARCH[site['school']] < site['level']:
            unknownSites.append(site)


#########################
# Normalize probabilities

allSiteNorm = sum((site['rarity'] for site in allSites))

normCoeff = SITEFREQ/allSiteNorm

for site in unknownSites:
    site['chance'] = site['rarity']*normCoeff

newNorm = 1 - SITEFREQ + sum([site['chance'] for site in unknownSites])
complement = (1 - SITEFREQ) / newNorm
print(1-complement)
for site in unknownSites:
    site['chance'] /= newNorm


###############
# Print results

print('lvl\t1\t\t2\t\t3\t\t4')
for i, school in enumerate(SCHOOLS):
    # expect is [level1, level2, etc] and levelN is [schoolGems, otherGems]
    expect = [[0, 0], [0, 0], [0, 0], [0, 0]]
    for site in unknownSites:
        if site['school'] == i:
            expect[site['level']-1][0] += (site['chance'] * site['schoolGems']
                                           * UNFOUNDSITES)
            expect[site['level']-1][1] += (site['chance'] * site['otherGems']
                                           * UNFOUNDSITES)
    line = '\t'.join([str(e[0])[:5]+'/'+str(e[1])[:5] for e in expect])
    print(school+'\t'+line)
