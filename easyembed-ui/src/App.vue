<template>
  <div style="padding: 20px;">
    <h1>EasyEmbed</h1>

    <!-- File input -->
    <div>
      <label>Select File:</label><br>
      <input type="file" @change="handleFile" />
    </div>

    <br>

    <!-- Extended toggle -->
    <div>
      <label>
        <input type="checkbox" v-model="extended" />
        Enable Extended Codecs
      </label>
    </div>

    <br>

    <!-- Submit -->
    <button @click="submit" :disabled="!file">
      Convert
    </button>

    <p>{{ status }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      file: null,
      extended: false,
      status: ""
    }
  },

  methods: {
    handleFile(event) {
      this.file = event.target.files[0]
    },

    async submit() {
      if (!this.file) {
        this.status = "Please select a file first."
        return
      }

      const formData = new FormData()
      formData.append("file", this.file)

      this.status = "Uploading..."

      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData
      })
      
      if (!res.ok) {
        let errorMessage = "Upload failed."

        try {
          const err = await res.json()
          errorMessage = err.detail || errorMessage
        } catch (e) {}
        
        this.status = errorMessage
        return
      }

      const data = await res.json()

      console.log(data)
      this.status = "Processing..."
    }
  }
}
</script>