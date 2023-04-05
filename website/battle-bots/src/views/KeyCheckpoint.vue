<template>
<v-container>
    <v-layout align-center justify-center>
      <v-flex>
        <div v-if="!loading">
            <div style="height: 30vh" />
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
    import * as sampleJSON from "@/sampleData.json"

    export default {
        name: 'keyCheckpoint',
        computed: {
        },
        data() {
            return {
                gameID: null,
                loading: false,
                gameData: sampleJSON,
                gameIdEntryRules: [
                    value => {
                        if (value && Object.prototype.hasOwnProperty.call(this.gameData["games"], this.gameID) ) return true
                        return 'Invalid Game ID.'
                    },
                ],
            };
        },
        methods: {
            gameIDbuttonPress() {
                this.loading = true
                setTimeout(()=> {
                    if(!Object.prototype.hasOwnProperty.call(this.gameData["games"], this.gameID)) {
                        console.log(`Game ID "${this.gameID}" not found.`);
                        this.loading = false;
                        // add some notifier code?
                        return;
                    }

                    this.$router.push({name: 'viewBoard', params: { gameID: this.gameID, gameData: this.gameData }});
                    this.loading = false;
                }, 500)
            },
            debug(){
                console.log(this.limitGroupCapacity);
            }
            
        }
    }

</script>
