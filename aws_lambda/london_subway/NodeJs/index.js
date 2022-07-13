//@ts-check

const https = require('https');

/**
 * @param {!Object} req Cloud Function request context.
 * @param {!Object} res Cloud Function response context.
 */
exports.handler = (req, res) => {
    // Get a bearer token from twitter
    console.log('Starting the handler execution')

    console.log('Getting incoming parameters ...')
    console.log('1.Consumer Key = ' + req.body.secrets.consumerKey)
    console.log('1.Consumer Secret = ' + req.body.secrets.consumerSecret)

    let post = https.request({
        method: 'GET',
        hostname: 'api.tfl.gov.uk',
        path: '/line/mode/tube/status',
        headers: {
            'Content-Type': 'application/json',
        }
    }, postRes => {
        var reply = ''
        postRes.setEncoding('utf8')
        postRes.on('data', chunk => reply += chunk)
        postRes.on('end', () => withReponse(JSON.parse(reply)))
    })
    
    post.on('error', e => console.log(`Problem with request ${e}`))
    post.write('grant_type=client_credentials')
    post.end()
    
    // Get the TFL reponse and collect the data
    function withReponse(timeline) {
        console.log(`...got ${timeline.length} line status data, sending to Fivetran.`)

        let since_id = null

        // Reformat Twitter's response into nice, flat tables
        let tflLineStatus = []
        for (let t of timeline) {
            // Remember the first id we encounter, which is the most recent
            if (since_id == null) {
                since_id = t.id
            }

            console.log(`Selecting the schema values`);

            // Add all tflLineStatus
            tflLineStatus.push({
                linename: t.id,
                linestatus: t.lineStatuses[0].statusSeverityDescription,
                timestamp : t.created
            })
        }
        // Send JSON response back to Fivetran
        res.header("Content-Type", "application/json")
        res.status(200).send({
            // Remember the most recent id, so our requests are incremental
            state: {
                since_id: since_id == null ? req.state.since_id : since_id
            },
            // Fivetran will use these primary keys to perform a `merge` operation,
            // so even if we send the same row twice, we'll only get one copy in the warehouse
            schema : {
                tflLineStatus : {
                    primary_key : ['linename']
                }
            },
            // Insert these rows into my warehouse
            insert: {
                tflLineStatus: tflLineStatus
            },
            // If this is true, Fivetran will immediately call this function back for more data
            // This is useful to page through large collections
            hasMore : false
        })
    }
}