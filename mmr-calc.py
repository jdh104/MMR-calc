#!/usr/bin/env python3

PRGM_AUTHOR =  "@JTweenr"
PRGM_VERSION = "2018.1.3"
PRGM_TITLE =   "Ranked-Play MMR Algorithm plus TestBench designed for Call of Duty: WWII"

###############################
## Begin Customization Block ##
###############################

MMR_DEF_INCREASE =  26  # Default MMR increase for winning
MMR_DEF_DECREASE = -24  # Default MMR decrease for losing
MMR_MAX_INCREASE =  60  # Maximum MMR increase for winning
MMR_MAX_DECREASE = -40  # Maximum MMR decrease for losing
MMR_MIN_INCREASE =  15  # Minimum MMR increase for winning
MMR_MIN_DECREASE =  -5  # Minimum MMR decrease for losing
MMR_QUIT_PENALTY = -75  # Static MMR penalty for quitting

TEAM_AVG_WEIGHT  =   5  # Weight value for performance relative to teammates 
OPNT_AVG_WEIGHT  =   3  # Weight value for performance relative to opponents

SCORE_GAIN = 2.2  # Gain value for score (increase slightly if players are not being awarded enough for score)
KILL_GAIN  = 2.9  # Gain value for kills (increase slightly if players are not being awarded enough for kills)
OBJ_GAIN   = 0.9  # Gain value for objec (increase slightly if players are not being awarded enough for objective play)

##############################
## End Customization Block ###
##############################
##############################
## Begin Data Input Block ####
##############################

SCORE = [6, 0]
# [TEAM_1_SCORE, TEAM_2_SCORE]

#----------------MMR---TIM--SCO--KIL--OBJ
STAT_MATRIX = [[[1647, 320, 850, 7,   1],
                [1784, 320, 680, 6,   0],
                [1472, 320, 625, 6,   0],
                [1817, 320, 605, 5,   0]],  # Team 1
#             ------------------------------
               [[1604, 320, 300, 3,   0],
                [1666, 320, 140, 1,   0],
                [1611, 320, 140, 1,   0], 
                [1888, 320, 140, 1,   0]]]  # Team 2

# Columns are: MMR, Time Played, Score, Kills, Objective
### Time Played is in seconds
### Objective is sum of all objective count (Time in hardpoint; captures and returns in ctf; plants and defuses in snd)
### Objective play does not need to be weighted (Count HP time in seconds)
### Do not count "defends" in Hardpoint
# Teams separated by comment line

##############################
## End Data Input Block ######
##############################
##############################
## Begin Method Definitions ##
##############################

def getMmrOf(team, player):
	return STAT_MATRIX[team][player][0]

def isQuitter(team, player):
	return STAT_MATRIX[team][player][1] < GAME_TIME

def getTimeOf(team, player):
	return STAT_MATRIX[team][player][1]

def getScoreOf(team, player):
	return STAT_MATRIX[team][player][2]

def getKillsOf(team, player):
	return STAT_MATRIX[team][player][3]

def getObjecOf(team, player):
	return STAT_MATRIX[team][player][4]

def isPartied(team, player):
	return STAT_MATRIX[team][player][5]

def myTeamsAvgKills(i):
	return TEAM_KILL_SUMS[i] / 4

def myTeamsAvgScore(i):
	return TEAM_SCORE_SUMS[i] / 4

def myTeamsAvgObj(i):
	return TEAM_OBJ_SUMS[i] / 4

def theirTeamsAvgKills(i):
	return TEAM_KILL_SUMS[(i+1)%2] / 4

def theirTeamsAvgScore(i):
	return TEAM_SCORE_SUMS[(i+1)%2] / 4

def theirTeamsAvgObj(i):
	return TEAM_OBJ_SUMS[(i+1)%2] / 4

##########################################
## End Method Definitions ################
##########################################
##########################################
## Initialize Program using STAT_MATRIX ##
##########################################

if SCORE[0] > SCORE[1]:
	TEAM_1_VICTORY = True
	TEAM_2_VICTORY = False
	WINNING_TEAM = 0
	LOSING_TEAM = 1
else:
	TEAM_1_VICTORY = False
	TEAM_2_VICTORY = True
	WINNING_TEAM = 1
	LOSING_TEAM = 0

# Construct auxilliary lists
MMR_LIST = [getMmrOf(int(i/4),i%4) for i in range(8)]
SCORE_LIST = [getScoreOf(int(i/4),i%4) for i in range(8)]
TIME_LIST = [getTimeOf(int(i/4),i%4) for i in range(8)]
KILLS_LIST = [getKillsOf(int(i/4),i%4) for i in range(8)]
OBJ_LIST = [getObjecOf(int(i/4),i%4) for i in range(8)]
ADJ_LIST = [0 for i in range(8)]

TEAM_MMR_SUMS = [sum([MMR_LIST[i] for i in range(4)]), sum([MMR_LIST[i+4] for i in range(4)])]
TEAM_SCORE_SUMS = [sum([SCORE_LIST[i] for i in range(4)]), sum([SCORE_LIST[i+4] for i in range(4)])]
TEAM_KILL_SUMS = [sum([KILLS_LIST[i] for i in range(4)]), sum([KILLS_LIST[i+4] for i in range(4)])]
TEAM_OBJ_SUMS = [sum([OBJ_LIST[i] for i in range(4)]), sum([OBJ_LIST[i+4] for i in range(4)])]
TEAM_TIME_SUMS = [sum([TIME_LIST[i] for i in range(4)]), sum([TIME_LIST[i+4] for i in range(4)])]

# Initialize auxilliary statistics
WEIGHT_SUM = TEAM_AVG_WEIGHT + OPNT_AVG_WEIGHT
GAIN_SUM = KILL_GAIN + SCORE_GAIN + OBJ_GAIN
GAME_TIME = max(TIME_LIST)
HIGH_MMR = max(MMR_LIST)

SCORE_SUM = sum(TEAM_SCORE_SUMS)
KILLS_SUM = sum(TEAM_KILL_SUMS)
OBJ_SUM = sum(TEAM_OBJ_SUMS)

AVG_MMR = int(sum(MMR_LIST) / 8)
AVG_SCORE = int(SCORE_SUM / 8)
AVG_KILLS = int(KILLS_SUM / 8)
AVG_OBJ = int(OBJ_SUM / 8)

#################################
## End Initialization Block #####
#################################
#################################
######## Begin Algorithm ##################################################

def interpolate(x, x0, x1, y0, y1): # Use linear regression to map an x value to a curve
	if x0 == x1:
		return 0
	else:
		return (y0 + (x - x0) * ((y1 - y0) / (x1 - x0)))

def getLmar(team_id):
	if WINNING_TEAM == team_id:
		return (MMR_MIN_INCREASE - MMR_DEF_INCREASE)
	else: 
		return (MMR_MAX_DECREASE - MMR_DEF_DECREASE)

def getHmar(team_id):
	if WINNING_TEAM == team_id:
		return (MMR_MAX_INCREASE - MMR_DEF_INCREASE)
	else:
		return (MMR_MIN_DECREASE - MMR_DEF_DECREASE)

for team_id in range(2):

	ktut = myTeamsAvgKills(team_id)     # Upper-threshold for kills relative to teammates
	kout = theirTeamsAvgKills(team_id)  # Upper-threshold for kills relative to opponents
	stut = myTeamsAvgScore(team_id)     # Upper-threshold for score relative to teammates
	sout = theirTeamsAvgScore(team_id)  # Upper-threshold for score relative to opponents
	otut = myTeamsAvgObj(team_id)       # Upper-threshold for obj relative to teammates
	oout = theirTeamsAvgObj(team_id)    # Upper-threshold for obj relative to opponents

	ktlt = -ktut  # Lower-threshold for kills relative to teammates
	kolt = -kout  # Lower-threshold for kills relative to opponents
	stlt = -stut  # Lower-threshold for score relative to teammates
	solt = -sout  # Lower-threshold for score relative to opponents
	otlt = -otut  # Lower-threshold for obj relative to teammates
	oolt = -oout  # Lower-threshold for obj relative to opponents

	lmar = getLmar(team_id) # Low Range for MMR adjustment
	hmar = getHmar(team_id) # High range for MMR adjustment

	for player_id in range(4):
	
		delta_kt = getKillsOf(team_id, player_id) - myTeamsAvgKills(team_id)
		delta_ko = getKillsOf(team_id, player_id) - theirTeamsAvgKills(team_id)
		delta_st = getScoreOf(team_id, player_id) - myTeamsAvgScore(team_id)
		delta_so = getScoreOf(team_id, player_id) - theirTeamsAvgScore(team_id)
		delta_ot = getObjecOf(team_id, player_id) - myTeamsAvgObj(team_id)
		delta_oo = getObjecOf(team_id, player_id) - theirTeamsAvgObj(team_id)

		kt_bonus = interpolate(delta_kt, ktlt, ktut, lmar, hmar) * KILL_GAIN * TEAM_AVG_WEIGHT / GAIN_SUM / WEIGHT_SUM
		ko_bonus = interpolate(delta_ko, kolt, kout, lmar, hmar) * KILL_GAIN * OPNT_AVG_WEIGHT / GAIN_SUM / WEIGHT_SUM
		st_bonus = interpolate(delta_st, stlt, stut, lmar, hmar) * SCORE_GAIN * TEAM_AVG_WEIGHT / GAIN_SUM / WEIGHT_SUM
		so_bonus = interpolate(delta_so, solt, sout, lmar, hmar) * SCORE_GAIN * OPNT_AVG_WEIGHT / GAIN_SUM / WEIGHT_SUM
		ot_bonus = interpolate(delta_ot, otlt, otut, lmar, hmar) * OBJ_GAIN * TEAM_AVG_WEIGHT / GAIN_SUM / WEIGHT_SUM
		oo_bonus = interpolate(delta_oo, oolt, oout, lmar, hmar) * OBJ_GAIN * OPNT_AVG_WEIGHT / GAIN_SUM / WEIGHT_SUM

		kill_mmr_bonus = kt_bonus + ko_bonus
		score_mmr_bonus = st_bonus + so_bonus
		obj_mmr_bonus = ot_bonus + oo_bonus

		total_mmr_bonus = kill_mmr_bonus + score_mmr_bonus + obj_mmr_bonus
		time_factor = (TEAM_TIME_SUMS[team_id] - getTimeOf(team_id, player_id)) / (TEAM_TIME_SUMS[(team_id+1)%2] - GAME_TIME)
		rank_factor = getMmrOf(team_id, player_id) / AVG_MMR
		aux_factor = time_factor * rank_factor

		if isQuitter(team_id, player_id):
			ADJ_LIST[team_id * 4 + player_id] = MMR_QUIT_PENALTY
		elif WINNING_TEAM == team_id:
			ADJ_LIST[team_id * 4 + player_id] = int(max(MMR_MIN_INCREASE, min(MMR_MAX_INCREASE, (MMR_DEF_INCREASE + total_mmr_bonus) / aux_factor)))
		else:
			ADJ_LIST[team_id * 4 + player_id] = int(max(MMR_MAX_DECREASE, min(MMR_MIN_DECREASE, (MMR_DEF_DECREASE + total_mmr_bonus) * aux_factor)))

		## DEBUG BLOCK #########################
		# print("team=", team_id)              #
		# print("player=", player_id)          #
		# print("kt=", kt_bonus)               #
		# print("ko=", ko_bonus)               #
		# print("st=", st_bonus)               #
		# print("so=", so_bonus)               #
		# print("ot=", ot_bonus)               #
		# print("oo=", oo_bonus)               #
		# print("tf=", time_factor)            #
		# print("rf=", rank_factor)            #
		# print("af=", aux_factor, end="\n\n") #
		## DEBUG BLOCK #########################

######### End Algorithm ###################################################
#################################
## Begin Reporting Section ######
#################################

print("MMR\tTIM\tSCO\tKIL\tOBJ\tADJ")
for i in range(2):
	print("")
	for j in range(4):
		for k in range(5):
			print(STAT_MATRIX[i][j][k], end="\t")
		print(ADJ_LIST[i*4+j])

###########################
## End Reporting Section ##
###########################
