<template>
  <v-container>
    <div class="d-flex align-center justify-center">
        <v-card class="mx-auto" max-width="75%">
            <div class="pa-10 text-center">
                <div v-for="(row, index) in board" :key="index">
                    <div class="d-flex justify-center">
                        <span v-for="(space, index2) in row" :key="index2">
                            <v-img v-if="board[index][index2] == -1" src="@/assets/empty_slot.png"/>
                            <v-img v-if="board[index][index2] == 0" src="@/assets/red_slot.png"/>
                            <v-img v-if="board[index][index2] == 1" src="@/assets/yellow_slot.png"/>
                        </span>
                    </div>
                </div>
            </div>
        </v-card>
    </div>
  </v-container>
</template>


<script>
    export default {
        name: 'ConnectFour',
        data() {
            return {
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
            editSpot(row, col, color){
                if (color == 'red')
                    self.board[row][col] = 0;
                else if (color == 'yellow')
                    self.board[row][col] = 1;
                else
                    self.board[row][col] = -1;
            },
            placeNewChip(col, color){
                let colorNum = 0;
                if (color == 'red')
                    colorNum = 0;
                else if (color == 'yellow')
                    colorNum = 1;
                else
                    throw console.error("Invalid parameter on chip placement.");

                let targetRow = -1;
                for (let i = 5; i >= 0; i--) {
                    if (self.board[i][col] == -1){
                        targetRow = i;
                        break;
                    }
                }
                self.board[targetRow][col] = colorNum;
            },
            setBoard(newBoard){ // newBoard param should be a 2D array, dimensions 6 x 7
                self.board = newBoard;
            }

        }
    }
</script>