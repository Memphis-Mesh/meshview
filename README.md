# Meshview, but ready for cloud

tl;dr this is [meshview](https://github.com/pablorevilla-meshtastic/meshview) but with a few tweaks to make it run more easily in the cloud.

## What's different

- Landed [vidplace7's PR](https://github.com/pablorevilla-meshtastic/meshview/pull/25) to improve the containerfile/dockerfile and general container practices
- Added automation to publish builds

## Run with docker-compose

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to point to your local `config.ini` and `packets.db` files.

Create `packets.db` file if it does not exist, before passing to the container.
```bash
touch ./packets.db
```
### Start compose

From the location where `meshview` was closed.
Start compose in the background:
```bash
docker compose up -d
```


## Run with kubernetes (k8s)

Here is a helmfile example of deploying meshview:

```yaml
---
repositories:
  - name: bjw-s
    url: https://bjw-s-labs.github.io/helm-charts
  - name: incubator
    url: https://charts.helm.sh/incubator
releases:
  - name: &resources-name meshview-resources
    namespace: &namespace meshview
    chart: incubator/raw
    version: 0.2.5
    installed: true
    disableValidation: true
    values:
      - resources:
        - apiVersion: v1
          kind: ConfigMap
          metadata:
            name: &config-name config
            namespace: *namespace
          data:
            config.ini: |
                # -------------------------
                # Server Configuration
                # -------------------------
                [server]
                # The address to bind the server to. Use * to listen on all interfaces.
                bind = *

                # Port to run the web server on.
                port = 8081

                # Path to TLS certificate (leave blank to disable HTTPS).
                tls_cert =

                # Path for the ACME challenge if using Let's Encrypt.
                acme_challenge =


                # -------------------------
                # Site Appearance & Behavior
                # -------------------------
                [site]
                # The domain name of your site.
                domain =

                # Site title to show in the browser title bar and headers.
                title = Memphis Mesh

                # A brief message shown on the homepage.
                message = Real time data from around Memphis and beyond

                # Enable or disable site features (as strings: "True" or "False").
                nodes = True
                conversations = True
                everything = True
                graphs = True
                stats = True
                net = True
                map = True
                top = True

                # Map boundaries (used for the map view).
                map_top_left_lat = 35.6
                map_top_left_lon = -90.5
                map_bottom_right_lat = 34.7
                map_bottom_right_lon = -89.3

                # Weekly net details
                weekly_net_message = Weekly Mesh check-in. We will keep it open on every Wednesday from 5:00pm for checkins. The message format should be (LONG NAME) - (CITY YOU ARE IN) #BayMeshNet.
                net_tag = #MemphisMeshNet


                # -------------------------
                # MQTT Broker Configuration
                # -------------------------
                [mqtt]
                # MQTT server hostname or IP.
                server = mqtt.meshtastic.org

                # Topics to subscribe to (as JSON-like list, but still a string).
                topics = ["msh/US/memphisme.sh/#"]

                # Port used by MQTT (typically 1883 for unencrypted).
                port = 1883

                # MQTT username and password.
                username = meshdev
                password = large4cats


                # -------------------------
                # Database Configuration
                # -------------------------
                [database]
                # SQLAlchemy connection string. This one uses SQLite with asyncio support.
                connection_string = sqlite+aiosqlite:///../apppackets/packets.db
  - name: meshview
    namespace: *namespace
    chart: bjw-s/app-template
    version: 3.7.3
    needs:
      - *resources-name
    installed: true
    values:
      - controllers:
          main:
            strategy: Recreate
            containers:
              main:
                image:
                  repository: ghcr.io/memphis-mesh/meshview
                  tag: latest
                  pullPolicy: IfNotPresent
                env:
                  - name: TZ
                    value: America/Chicago
        service:
          main:
            controller: main
            ports:
              http:
                port: 8081

        ingress:
          main:
            className: nginx
            hosts:
              - host: &host meshview.home.arpa
                paths:
                  - path: /
                    pathType: Prefix
                    service:
                      identifier: main
                      port: http
            tls:
              - hosts:
                  - *host
                secretName: "meshview-tls"
        persistence:
          packets:
            enabled: true
            type: persistentVolumeClaim
            accessMode: ReadWriteOnce
            size: 64Gi
            # storageClass: myStorageClass
            advancedMounts:
              main:
                main:
                  # - path: /app/packets.db
                  #   subPath: packets.db
                  - path: /apppackets
          config:
            enabled: true
            type: configMap
            name: *config-name
            advancedMounts:
              main:
                main:
                  - path: /etc/meshview/config.ini
                    subPath: config.ini

```
