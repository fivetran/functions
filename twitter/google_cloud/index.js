//@ts-check

const https = require('https');

/**
 * @param {!Object} req Cloud Function request context.
 * @param {!Object} res Cloud Function response context.
 */
exports.handler = (req, res) => {
    // Get a bearer token from twitter
    console.log('Getting access token from twitter...')
    let post = https.request({
        method: 'POST',
        hostname: 'api.twitter.com',
        path: '/oauth2/token',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Content-Length': 'grant_type=client_credentials'.length,
            'Authorization': 'Basic ' + Buffer.from(`${req.body.secrets.consumerKey}:${req.body.secrets.consumerSecret}`, 'utf8').toString('base64')
        }
    }, postRes => {
        var reply = ''
        postRes.setEncoding('utf8')
        postRes.on('data', chunk => reply += chunk)
        postRes.on('end', () => withAuth(JSON.parse(reply)))
    })
    post.on('error', e => console.log(`Problem with request ${e}`))
    post.write('grant_type=client_credentials')
    post.end()
    
    // Once we get an auth token, use it to request Justin Bieber's timeline
    function withAuth(auth) {
        console.log('...got access token from twitter, fetching tweets...')
        var path = '/1.1/statuses/user_timeline.json?screen_name=justinbieber'
        // If this is not the first request, append since_id={since_id} to the request path
        if (req.body.state.since_id != null) {
            console.log(`...getting new tweets since id ${req.body.state.since_id}...`)
            path += '&since_id=' + req.body.state.since_id
        }
        // Get recent tweets
        let get = https.get({
            hostname: 'api.twitter.com',
            path: path,
            headers: {
                'Authorization': 'Bearer ' + auth.access_token
            }
        }, getRes => {
            var reply = ''
    
            getRes.on('data', chunk => reply += chunk)
            getRes.on('end', () => withTweets(JSON.parse(reply)))
        })
    }
    
    // Once we get Justin Bieber's timeline, use it to upsert data into our warehouse
    function withTweets(timeline) {
        console.log(`...got ${timeline.length} tweets, sending to Fivetran.`)
        // Keep track of the most recent id, so future updates are incremental
        let since_id = null
        // Reformat Twitter's response into nice, flat tables
        let tweets = []
        let users = []
        for (let t of timeline) {
            // Remember the first id we encounter, which is the most recent
            if (since_id == null) {
                since_id = t.id
            }
            // Add all tweets
            tweets.push({
                id: t.id,
                user_id: t.user.id,
                text: t.text
            })
            // Add user info
            // Don't worry about duplication--Fivetran will take care of this for us
            users.push({
                id: t.user.id,
                name: t.user.name,
                screen_name: t.user.screen_name
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
                tweets : {
                    primary_key : ['id']
                },
                users: {
                    primary_key: ['id']
                }
            },
            // Insert these rows into my warehouse
            insert: {
                tweets: tweets,
                users: users
            },
            // If this is true, Fivetran will immediately call this function back for more data
            // This is useful to page through large collections
            hasMore : false
        })
    }
}