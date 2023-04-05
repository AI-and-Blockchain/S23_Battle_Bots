<template>
  <v-container>
    <div class="align-center justify-center pb-5">
        <v-card class="pa-10">
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
    </div>
    <v-row>
        <v-col cols="3" />

        <v-col cols="1">
            <div class="d-flex justify-center">
                <div class="d-flex justify-center">
                    <v-text-field type="number" oninput="if(this.value < 0) this.value = 0; else if(this.value > this.totalTurnCount) this.value = this.totalTurnCount;" v-model="turnNumber" variant="outlined"/>
                </div>
            </div>
        </v-col>
        <v-col cols="1">
            <div class="d-flex justify-center">
                <div class="d-flex justify-center">
                    of {{ totalTurnCount }}
                </div>
            </div>
        </v-col>
        <v-col cols="2" />
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
    export default {
        name: 'ConnectFour',
        data() {
            return {
                turnNumber: 1,
                totalTurnCount: this.gameData["games"][this.gameID]["turns"].length,
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
            backOneTurn(){
                this.removeTopChip(this.gameData["games"][this.gameID]["turns"][this.turnNumber - 1]);
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
                console.log(this.gameData["games"][this.gameID]["turns"][this.turnNumber - 1])
                this.placeNewChip(this.gameData["games"][this.gameID]["turns"][this.turnNumber - 1], (this.turnNumber - 1) % 2)
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
            this.placeNewChip(this.gameData["games"][this.gameID]["turns"][0], 0)
        },
        props: ['gameID', 'gameData']
    }
</script>