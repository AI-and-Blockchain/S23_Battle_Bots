<template>
  <v-container>
    <div style="height: 10vh" />
    <div class="align-center justify-center py-5">
        <v-row>
            <v-col cols="1">
                <div class="d-flex justify-center">
                    <div class="d-flex justify-center">
                        <v-btn @click="backButton()" dark color="secondary">
                            &lt; BACK
                        </v-btn>
                    </div>
                </div>
            </v-col>
            <v-col cols="8">
                <v-card class="pa-10" color="#443ED5">
                    <div class="pa-10 text-center">
                        <div v-for="(row, index) in board" :key="index">
                            <span class="">
                                <span v-for="(space, index2) in row" :key="index2">
                                    <img v-if="board[index][index2] == -1" src="@/assets/empty_slot.png"/>
                                    <img v-if="board[index][index2] == 0" src="@/assets/red_slot.png"/>
                                    <img v-if="board[index][index2] == 1" src="@/assets/yellow_slot.png"/>
                                </span>
                            </span>
                        </div>
                    </div>
                </v-card>
            </v-col>
            <v-col cols="3">
                <v-expansion-panels variant="inset">
                    <v-expansion-panel>
                        <v-expansion-panel-header>
                            Game Data
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                            Winner: {{ this.gameData[this.gameJSONIndex]["winner_id"] }} <br> 
                            Number of Turns: {{ this.totalTurnCount }} <br>

                        </v-expansion-panel-content>
                    </v-expansion-panel>

                    <v-expansion-panel>
                        <v-expansion-panel-header>
                            Player 1 Data
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                            Player 1 Name: {{ this.botData[this.playerOneBotDataJsonIndex]["name"] }} <br>
                            Player 1 ID: {{ this.botData[this.playerOneBotDataJsonIndex]["bot_id"] }} <br>
                            Games Won: {{ this.botData[this.playerOneBotDataJsonIndex]["win_count"] }} <br>
                            Games Played: {{ this.botData[this.playerOneBotDataJsonIndex]["total_games"] }} <br>
                            W/L Pct: {{ (this.botData[this.playerOneBotDataJsonIndex]["win_count"]) / this.botData[this.playerOneBotDataJsonIndex]["total_games"] }} <br>
                            Avg. Score: {{ this.botData[this.playerOneBotDataJsonIndex]["avg_reward"] }} <br>
                            Learning Rate: {{ (((this.botData[this.playerOneBotDataJsonIndex]["epsilon"] * 100) * 100) / 100).toFixed(2) }}%
                        </v-expansion-panel-content>
                    </v-expansion-panel>

                    <v-expansion-panel>
                        <v-expansion-panel-header>
                            Player 2 Data
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                            Player 1 Name: {{ this.botData[this.playerTwoBotDataJsonIndex]["name"] }} <br>
                            Player 1 ID: {{ this.botData[this.playerTwoBotDataJsonIndex]["bot_id"] }} <br>
                            Games Won: {{ this.botData[this.playerTwoBotDataJsonIndex]["win_count"] }} <br>
                            Games Played: {{ this.botData[this.playerTwoBotDataJsonIndex]["total_games"] }} <br>
                            W/L Pct: {{ (this.botData[this.playerTwoBotDataJsonIndex]["win_count"]) / this.botData[this.playerOneBotDataJsonIndex]["total_games"] }} <br>
                            Avg. Score: {{ this.botData[this.playerTwoBotDataJsonIndex]["avg_reward"] }} <br>
                            Learning Rate: {{ (((this.botData[this.playerTwoBotDataJsonIndex]["epsilon"] * 100) * 100) / 100).toFixed(2) }}%
                        </v-expansion-panel-content>
                    </v-expansion-panel>
                </v-expansion-panels>
            </v-col>
        </v-row>
        
    </div>
    <v-row>
        <v-col cols="1" />

        <v-col cols="2">
            <div class="d-flex justify-center">
                <div class="d-flex justify-center">
                    <h1> Turn {{ turnNumber }} of {{ totalTurnCount }} </h1>
                </div>
            </div>
        </v-col>
        <v-col cols="4" />
        <v-col cols="1">
            <div class="d-flex justify-center">
                <div class="d-flex justify-center">
                    <v-btn @click="backOneTurn()" dark :disabled="this.turnNumber == 0" color="secondary">
                        <v-icon size="3vh" color="white"> mdi-arrow-left-drop-circle-outline </v-icon>
                    </v-btn>
                </div>
            </div>
        </v-col>
        <v-col cols="1">
            <div class="d-flex justify-center">
                <div class="d-flex justify-center">
                    <v-btn @click="forwardOneTurn()" dark :disabled="this.turnNumber == totalTurnCount" color="secondary">
                        <v-icon size="3vh" color="white"> mdi-arrow-right-drop-circle-outline </v-icon>
                    </v-btn>
                </div>
            </div>
        </v-col>

        <v-col cols="3" />
    </v-row>
  </v-container>
</template>


<script>
    import * as botJSON from "@/../../q_learning/bots.json"

    export default {
        name: 'ConnectFour',
        data() {
            return {
                botData: botJSON,
                playerOneBotDataJsonIndex: -1,
                playerTwoBotDataJsonIndex: -1,
                turnNumber: 1,
                totalTurnCount: this.gameData[this.gameJSONIndex]["actions"].length,
                board: [ [-1, -1, -1, -1, -1, -1, -1],
                         [-1, -1, -1, -1, -1, -1, -1],
                         [-1, -1, -1, -1, -1, -1, -1],
                         [-1, -1, -1, -1, -1, -1, -1],
                         [-1, -1, -1, -1, -1, -1, -1],
                         [-1, -1, -1, -1, -1, -1, -1] ] // [0][1] -> top row, second column
                                                        // -1 => empty, 0 -> red, 1 -> yellow
            };
        },
        methods: {
            backButton(){
                this.$forceUpdate();
                this.$router.push({name: 'keyCheckpoint'});
                this.$forceUpdate();
            },
            backOneTurn(){
                this.removeTopChip(this.gameData[this.gameJSONIndex]["actions"][this.turnNumber - 1]);
                this.turnNumber--;
            },
            editSpot(row, col, color){
                if (color == 'red')
                    this.board[row][col] = 0;
                else if (color == 'yellow')
                    this.board[row][col] = 1;
                else
                    this.board[row][col] = -1;
            },
            forwardOneTurn(){
                this.turnNumber++;
                console.log(this.gameData[this.gameJSONIndex]["actions"][this.turnNumber - 1])
                this.placeNewChip(this.gameData[this.gameJSONIndex]["actions"][this.turnNumber - 1], (this.turnNumber - 1) % 2)
            },
            placeNewChip(col, colorNum){
                if (this.board[1][col] != -1){
                    console.log("Column unavailable");
                    return;
                } // THIS MIGHT BE BUGGY

                let targetRow = -1;
                for (let i = 5; i > 0; i--) {
                    if (this.board[i][col] == -1){
                        targetRow = i;
                        break;
                    }
                }
                this.board[targetRow][col] = colorNum;
                this.$forceUpdate();
            },
            removeTopChip(col){
                let targetRow = -1;
                for (let i = 5; i > 0; i--) {
                    if (this.board[i][col] == -1){
                        targetRow = i + 1;
                        break;
                    }
                }
                this.board[targetRow][col] = -1;
                this.$forceUpdate();
            },
            setBoard(newBoard){ // newBoard param should be a 2D array, dimensions 6 x 7
                this.board = newBoard;
            }
        },
        mounted() {
            this.placeNewChip(this.gameData[this.gameJSONIndex]["actions"][0], 0)

            for (let i = 0; i < this.botData.length; i++) {
                if (this.botData[i]["bot_id"] == this.gameData[this.gameJSONIndex]["player_1_id"]){
                    this.playerOneBotDataJsonIndex = i;
                }
                else if (this.botData[i]["bot_id"] == this.gameData[this.gameJSONIndex]["player_2_id"]){
                    this.playerTwoBotDataJsonIndex = i;
                }
            }
        },
        props: ['gameJSONIndex', 'gameData']
    }
</script>