module.exports={
    devServer:{
        proxy:{
            ["/python"]:{
                target:'http://127.0.0.1:5000',
                changeOrigin:true,
                pathRewrite: {
                    ['^' + "/python"]: ''
                }
            }
        }
    }
}