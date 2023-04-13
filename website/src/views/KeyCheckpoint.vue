<template>
<v-container>
    <v-layout align-center justify-center>
      <v-flex>
        <div v-if="!loading">
            <div class="d-flex align-items-center justify-content-center" style="height: 40vh">
                <div v-if="showGameNotFoundAlert" class="pt-10">
                    <div style="height: 10vh" />
                    <v-alert color="#D31414" type="warning">
                        The Game ID you entered  was not found. Please try again with another ID.
                    </v-alert>
                </div>
            </div>
            <div class="d-flex align-items-center justify-content-center">
                <h1>Enter Game ID:</h1>
            </div>
            <div class="d-flex align-items-center justify-center pb-5">
                <div class="d-flex justify-center text-center">
                    <v-text-field v-model="gameID" label="Game ID" :rules="gameIdEntryRules" variant="outlined" />
                </div>
            </div>
            <div class="pt-5 pb-5 d-flex justify-center">
                <v-btn @click="gameIDbuttonPress()" :disabled="gameID == null || gameID == ''">
                    <v-icon size="2vh" color="white" type="submit">Submit</v-icon>
                </v-btn>
            </div>
        </div>
        <div v-else>
            <div style="height: 5vh" />
            <img src="@/assets/loading.gif"/> 
        </div>
      </v-flex>
    </v-layout>
  </v-container>
  
</template>

<script>
    import * as allGameData from "@/../../q_learning/games.json"

    export default {
        name: 'keyCheckpoint',
        computed: {
        },
        data() {
            return {
                gameID: null,
                loading: false,
                gameData: allGameData,
                showGameNotFoundAlert: false,
                gameIdEntryRules: [
                    value => {
                        if (value) return true
                        return 'Invalid Game ID.'
                    },
                ],
            };
        },
        methods: {
            gameIDbuttonPress() {
                this.loading = true
                setTimeout(()=> {
                    let gameIndex = -1;
                    for (let i = 0; i < this.gameData.length; i++){
                        if (this.gameData[i]['game_id'] == this.gameID){
                            gameIndex = i;
                            break;
                        }
                    }
                    
                    if (gameIndex == -1){
                        console.log(`Game ID "${this.gameID}" not found.`);
                        
                        this.showGameNotFoundAlert = true;
                        this.loading = false;
                        setTimeout(()=> {
                            this.showGameNotFoundAlert = false;
                        }, 4000)

                        
                        return;
                    }
                    this.$router.push({name: 'viewBoard', params: { gameJSONIndex: gameIndex, gameData: this.gameData }});
                    this.loading = false;
                }, 500)
            },
            debug(){
                console.log(this.limitGroupCapacity);
            }
            
        }
    }

</script>
